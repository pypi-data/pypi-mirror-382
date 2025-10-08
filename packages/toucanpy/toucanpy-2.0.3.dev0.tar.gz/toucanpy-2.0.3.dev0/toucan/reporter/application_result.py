from dataclasses import dataclass
from enum import Enum
from os.path import basename

from toucan.formats.format import ToucanFile


class Status(Enum):
    ERROR = 1
    NEW_OLD_VERSION = 2
    SUCCESS = 3


@dataclass(frozen=True)
class ApplicationResult:
    """
    A class representing the results of one application in a Toucan run.
    There are 3 major types or results:
        1. There was a new version and Toucan could generate test results
        2. There was no new version
        3. There was a new version but Toucan couldn't generate test results. Usually means a rollback happened, so the
        'new' version has a lower version number than a previously released version. In such a situation Toucan cannot
        install this version on the emulators and no testing happens.
    This class has three data fields:
       * the app name (mandatory)
       * the new version (optional)
       * the test results (optional)
    In case 1, all three fields are present. In case 2, only the app name is present. In case 3, app_name and
    new_version are present, but results are not.
    The results object reports all results: at the highest level it is a dict storing the test results for each file
    Toucan tested for this application: the key is the file name, the value contains the test results.
    The test results are a tuple:
    The first element is a bool reporting whether file recognition works.
    The second element is another dict, reporting on the result of all parsing rules that were checked. The key is the
    rule name, the value is a bool reporting whether the rule passed.
    """

    app_name: str
    new_version: str = None
    results: dict[ToucanFile, tuple[bool, dict[str, bool]]] = None
    run_status: Status = Status.SUCCESS

    def __post_init__(self):
        if not self.app_name:
            raise ValueError('Cannot create an ApplicationResult without an app name.')
        if self.results and not self.new_version:
            raise ValueError('An application version is required when reporting results.')
        if self.new_version and not self.results and self.run_status == Status.SUCCESS:
            raise ValueError('Run cannot be successful without results if there is a new version.')

    def has_new_version(self) -> bool:
        """
        Returns if there was a new version found for this application in this Toucan run.
        A new version could also be a rollback to a lower version number, see the class pydoc for more info.
        :return: True if a new version was detected.
        """
        return bool(self.new_version)

    def has_results(self) -> bool:
        """
        Returns whether Toucan could run any tests and report the findings.
        If no results are present, this usually is because no new version was detected. It could also be because a
        rollback to a lower version happened, see the class pydoc for more info.
        :return: True if there are Toucan test results
        """
        return bool(self.results)

    def has_complete_support(self) -> bool | None:
        """
        Returns whether all tests for all files for both recognition and parsing have passed.
        If no results are present, no return value can be given.
        :return: True if both recognition and parsing rules pass for all files. None if no results are present.
        """
        if self.results is None:
            return None
        return all(recognized and all(all_features.values()) for recognized, all_features in self.results.values())

    def all_files_recognized(self) -> bool | None:
        """
        Returns all files are recognized as expected.
        If no results are present, no return value can be given.
        :return: True if all files are recognized as expected. None if no results are present.
        """
        if self.results is None:
            return None
        return all(recognized for recognized, all_features in self.results.values())

    def all_parsing_rules_pass(self) -> bool | None:
        """
        Returns all parsing results are as expected for all files, as defined by each file's parsing rules.
        If no results are present, no return value can be given.
        :return: True if all parsing rules for all files pass. None if no results are present.
        """
        if self.results is None:
            return None
        return all(all(all_features.values()) for recognized, all_features in self.results.values())

    def all_unrecognized_files(self) -> list[ToucanFile]:
        """
        :return: a list of all files that were not recognized as expected. Empty list if no results are present.
        """
        if self.results is None:
            return []
        return [toucan_file for toucan_file, result in self.results.items() if not result[0]]

    def all_recognized_files(self) -> list[ToucanFile]:
        """
        :return: a list of all files that were recognized as expected. Empty list if no results are present.
        """
        if self.results is None:
            return []
        return [file_name for file_name, result in self.results.items() if result[0]]

    def all_failed_rules(self) -> dict[ToucanFile, list[str]]:
        """
        :return: a list of all failed rules
        """
        all_failed_rules = {}
        if self.results:
            for file_name in self.results.keys():
                parsing_results = self.results[file_name][1]
                failed_rules = [rule_name for rule_name, result in parsing_results.items() if not result]
                if failed_rules:
                    all_failed_rules[file_name] = failed_rules
        return all_failed_rules

    def all_passed_rules(self) -> dict[ToucanFile, list[str]]:
        """
        :return: a list of all failed rules
        """
        all_failed_rules = {}
        if self.results:
            for file_name in self.results.keys():
                parsing_results = self.results[file_name][1]
                failed_rules = [rule_name for rule_name, result in parsing_results.items() if result]
                if failed_rules:
                    all_failed_rules[file_name] = failed_rules
        return all_failed_rules

    @classmethod
    def error(cls, app_name: str, new_version: str = None):
        return ApplicationResult(app_name, new_version, run_status=Status.ERROR)

    @classmethod
    def new_old_version(cls, app_name: str, new_version: str):
        """
        Method to create an ApplicationResult when the run has a new version but is a lower version than the previous
        version.
        """
        return ApplicationResult(app_name, new_version, run_status=Status.NEW_OLD_VERSION)


def pretty_print(results: list[ApplicationResult]) -> str:
    """
    Pretty print the application results.

    :param results: the application results
    :return: pretty printed results
    """
    result_prints = []
    for result in results:
        if result.new_version:
            header = f'{result.app_name} v{result.new_version} - Run status: {result.run_status}'
        else:
            header = f'{result.app_name} - no new version - Run status: {result.run_status}'
        line = '=' * len(header)
        files = []
        if result.results:
            for toucan_file, results in result.results.items():
                files.append(f'{basename(toucan_file.file_path)}\n\tRecognition: {"ok" if results[0] else "FAILED"}')
                rule_results = '\n'.join(
                    [f'\t{rulename}: {"ok" if passed else "FAILED"}' for rulename, passed in results[1].items()]
                )
                files.append(rule_results)
        else:
            files.append('-no results-')
        files = '\n'.join(files)
        result_prints.append(f'{header}\n{line}\n{files}')
    return '\n'.join(result_prints)
