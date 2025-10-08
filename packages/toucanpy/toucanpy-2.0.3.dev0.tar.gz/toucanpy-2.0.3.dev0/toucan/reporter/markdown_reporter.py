import os
import shutil
from pathlib import Path

import pandas as pd
from pandas import DataFrame

from toucan.reporter.application_result import ApplicationResult, Status
from toucan.reporter.git_utils import commit_push_daily, git_checkout_and_pull
from toucan.reporter.reporter import Reporter
from toucan.utils import PACKAGE_ROOT, logger
from toucan.utils.time_utils import get_current_date


DAILY_REPORT_TEMPLATE = PACKAGE_ROOT / 'utils' / 'readme_templates' / 'general_readme_template.md'
APP_REPORT_TEMPLATE = PACKAGE_ROOT / 'utils' / 'readme_templates' / 'app_readme_template.md'


class MarkdownReporter(Reporter):
    """
    A basic Reporter for Toucan, which reports Toucan results to a Markdown file in a given folder.
    There is a main report, giving an overview of all ToucanFormats, and more detailed reports on each
    specific ToucanFormat, which are stored in subfolders.
    The results are also stored in a CSV file, but this is meant as a technical archive, while the Markdown
    files are meant as a user-friendly representation.
    This class can also use Git version control to sync the reports with a remote git repository.
    """

    def __init__(
        self,
        report_root: Path,
        report_file_name: str = 'README.md',
        git_pull_and_push: bool = False,
        destination_branch: str = 'master',
    ):
        """
        Creates a MarkdownReporter given the preferred configuration options.
        :param report_root: MANDATORY: the root directory in which all results files will be stored.
        :param report_file_name: the file name of all report Markdown files. Default: README.md
        :param git_pull_and_push: Whether to commit and push all report files. Default: False.
        :param destination_branch: The branch on which changes should be commited and pushed to. Default: master
        """
        super().__init__(report_root)
        self.application_results = None
        self.report_file_name = report_file_name
        self.new_report_file_name = self._append_new_to_report_name(report_file_name)
        self.branch = destination_branch
        self.current_date = get_current_date()
        self.push_to_remote = git_pull_and_push

    def report_results(self, application_results: list[ApplicationResult]) -> None:
        self.report_daily(application_results)

    def report_daily(self, results: list[ApplicationResult]):
        if self.push_to_remote:
            git_checkout_and_pull(self.report_root, self.branch)

        self._daily_summary(results)

        for result in results:
            self._application_report(result)

        if self.push_to_remote:
            self._push_reports(self.report_root, self.report_file_name)

    @staticmethod
    def _check_all_applications_unique(results: list[ApplicationResult]):
        """
        Check if the application results do not contain duplicates.

        :param: results: list of ApplicationResults
        """
        if len(results) != len({r.app_name for r in results}):
            raise ValueError('Given ApplicationResults contain multiple entries for the same app.')

    def _daily_summary(self, results: list[ApplicationResult]):
        """
        Updates or creates a daily summary for a given list of ApplicationResults.
        This summary will only list for each application whether there was a new version, and whether all Toucan checks
        Passed or failed.
        """
        self._check_all_applications_unique(results)
        daily_report: Path = self.report_root / self.report_file_name
        daily_report_new: Path = self.report_root / self.new_report_file_name
        previous_section_path: Path = self.report_root / 'previous_days.csv'
        support_today = self._all_applications_supported(results)

        self.report_root.mkdir(parents=True, exist_ok=True)
        shutil.copy(DAILY_REPORT_TEMPLATE, daily_report_new)

        previous_section = self._load_previous_section(self._get_daily_summary_table(results), previous_section_path)

        aggregated_previous_section = self.aggregate_by_date(previous_section)
        previous_section_md = aggregated_previous_section.to_markdown(floatfmt='.1f')
        section_today = aggregated_previous_section.head(1).to_markdown(floatfmt='.1f')

        # write the app statuses to the daily_report
        replacements = {
            'CURRENT_DATE': self.current_date,
            'TABLE_TODAY': section_today,
            'TABLE_PREVIOUS': previous_section_md,
            'SUPPORT': support_today,
        }
        self._write_report_file(daily_report_new, DAILY_REPORT_TEMPLATE, replacements)
        os.rename(daily_report_new, daily_report)
        self._update_previous_section_file(previous_section, previous_section_path)
        return

    @staticmethod
    def _write_report_file(report_path: Path, template_path: Path, replacements: dict[str, str]):
        """
        Writes the report file. Takes the template and search replaces the placeholders.
        :param report_path: path to new report
        :param template_path: Path to the template file
        :param replacements: replacement dictionary with the placeholders as keys
        """
        with open(template_path) as template:
            contents = template.read()

            for search, replace in replacements.items():
                contents = contents.replace(search, replace)
            with open(report_path, 'w') as new_file:
                new_file.write(contents)

    @staticmethod
    def _load_previous_section(today_table_entry: DataFrame, previous_section_path: Path) -> DataFrame:
        """
        Load previous section from the csv file into a DataFrame. Add today's record to the DataFrame.
        :param today_table_entry: Results of today
        :param previous_section_path: path to previous section csv file
        :return: previous section dataframe
        """
        if os.path.exists(previous_section_path):
            prev_section = pd.read_csv(previous_section_path, dtype=str, keep_default_na=False)
        else:
            logger.warning(
                f'No previous section could be found at {previous_section_path}. Creating an empty DataFrame.'
            )
            prev_section = pd.DataFrame()
        # Add today's section
        return pd.concat([today_table_entry, prev_section], ignore_index=True)

    @staticmethod
    def aggregate_by_date(prev_section: DataFrame) -> DataFrame:
        """
        Aggregate the records with the same date.
        :param prev_section: previous section dataframe
        :return:
        """
        return (
            prev_section.groupby('Date')
            .agg(lambda entry: '<br />'.join(entry))
            .sort_values(by=['Date'], ascending=False)
        )

    @staticmethod
    def _update_previous_section_file(previous_section: DataFrame, previous_section_path: Path):
        previous_section.to_csv(f'{previous_section_path}', index=False)

    def _application_report(self, result: ApplicationResult):
        """
        Report daily results for the application to repo.
        :param result: Application result
        """
        app_report_root = self.report_root / result.app_name
        app_report = app_report_root / self.report_file_name
        app_report_new = app_report_root / self.new_report_file_name
        app_previous_section_path = app_report_root / 'previous_days.csv'

        # check whether directory and report file exist
        app_report_root.mkdir(parents=True, exist_ok=True)
        shutil.copy(APP_REPORT_TEMPLATE, app_report_new)

        if not result.has_new_version():
            new_version = '-'
            recognition = 'N/A'
            support = 'N/A'
        else:
            new_version = result.new_version
            recognition = (
                '✅' if result.all_files_recognized() else '❌' if result.all_files_recognized() is False else '❔'
            )
            support = (
                '✅' if result.all_parsing_rules_pass() else '❌' if result.all_parsing_rules_pass() is False else '❔'
            )

        previous_section = self._load_previous_section(self._get_app_summary_table(result), app_previous_section_path)
        aggregated_previous_section = self.aggregate_by_date(previous_section)
        # floatfmt is required to preserve the version numbers correctly. Tabulate rounds off floats,
        # even if they are strings
        previous_section_md = aggregated_previous_section.to_markdown(floatfmt='.1f')
        section_today = aggregated_previous_section.head(1).to_markdown(floatfmt='.1f')

        replacements = {
            'CURRENT_DATE': self.current_date,
            'NEW_VERSION': new_version,
            'RECOGNITION': recognition,
            'SUPPORT': support,
            'TABLE_TODAY': section_today,
            'TABLE_PREVIOUS': previous_section_md,
        }

        self._write_report_file(app_report_new, APP_REPORT_TEMPLATE, replacements)
        os.rename(app_report_new, app_report)
        self._update_previous_section_file(previous_section, app_previous_section_path)

    def _get_daily_summary_table(self, results: list[ApplicationResult]) -> DataFrame:
        """
        Returns a DataFrame with the results for each application for the daily summary.
        :param results: Application results
        :return: DataFrame with results
        """
        data = [
            {
                'Date': self.current_date,
                'App name': f'[{result.app_name}](./{result.app_name}/{self.report_file_name})',
                'Version': result.new_version if result.has_new_version() else '-',
                'Support': self._get_app_support_status(result),
                'Run status': self._status(result),
            }
            for result in results
        ]
        return pd.DataFrame(data)

    def _get_app_summary_table(self, result: ApplicationResult) -> DataFrame:
        """
        Returns a DataFrame with the results for the app summary.
        :param result: Application result
        :return: DataFrame with results
        """
        data = {
            'Date': self.current_date,
            'New version': result.new_version if result.has_new_version() else '-',
            'Recognition': self._recognition_entry(result),
            'Parsing': self._support_entry(result),
            'Run status': self._status(result),
        }
        return pd.DataFrame(data, index=[0])

    @staticmethod
    def _recognition_entry(result: ApplicationResult) -> str:
        if not result.has_new_version():
            return 'N/A'
        if result.all_files_recognized():
            return '✅'
        if not result.has_results():
            return '-'
        else:
            return ''.join(
                '❌ ' + toucan_file.file_path.name + '<br/>' for toucan_file in result.all_unrecognized_files()
            ) + ''.join('✅ ' + toucan_file.file_path.name + '<br/>' for toucan_file in result.all_recognized_files())

    @staticmethod
    def _support_entry(result: ApplicationResult) -> str:
        if not result.has_new_version():
            return 'N/A'
        if result.all_parsing_rules_pass():
            return '✅'
        if not result.has_results():
            return '-'
        else:
            support = ''
            for toucan_file, rules in result.all_failed_rules().items():
                for rule in rules:
                    support += f'❌ {toucan_file.file_path.name}:{rule}<br/>'
            for toucan_file, rules in result.all_passed_rules().items():
                for rule in rules:
                    support += f'✅ {toucan_file.file_path.name}:{rule}<br/>'
            return support

    @staticmethod
    def _get_app_support_status(result: ApplicationResult) -> str:
        if not result.has_new_version():
            return 'N/A'
        complete_support = result.has_complete_support()
        if complete_support is False:
            return '❌'
        if result.run_status is Status.NEW_OLD_VERSION:
            return '❔'
        if result.run_status is Status.ERROR:
            return '❔'
        return '✅'

    @staticmethod
    def _all_applications_supported(results: list[ApplicationResult]) -> str:
        has_any_non_results = Status.NEW_OLD_VERSION in [result.run_status for result in results]
        has_any_failed_results = False in [result.has_complete_support() for result in results]
        has_any_error_results = Status.ERROR in [result.run_status for result in results]

        if has_any_failed_results:
            return '❌'
        if has_any_error_results:
            return '⚠️'
        if has_any_non_results:
            return '❔'
        return '✅'

    @staticmethod
    def _push_reports(repo_root: Path, report_file_name):
        logger.info('Pushing results to daily...')
        # Push the new report
        commit_push_daily(repo_root, report_file_name)

    @staticmethod
    def _status(result) -> str:
        if result.run_status == Status.ERROR:
            return '⚠️'
        return '-'

    @staticmethod
    def _append_new_to_report_name(report_file_name: str | Path) -> Path:
        path = Path(report_file_name)
        return Path(f'{path.stem}_new{path.suffix}')
