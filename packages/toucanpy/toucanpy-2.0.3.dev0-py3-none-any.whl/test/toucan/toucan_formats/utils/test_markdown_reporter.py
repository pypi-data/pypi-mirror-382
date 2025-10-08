import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from freezegun import freeze_time
from parameterized import parameterized

from test import RESOURCE_ROOT
from toucan.formats.format import ToucanFileBuilder
from toucan.reporter.application_result import ApplicationResult
from toucan.reporter.markdown_reporter import MarkdownReporter

TEST_REPORT_ROOT = RESOURCE_ROOT / 'daily_summary'
WHATSAPP_REPORT_ROOT = TEST_REPORT_ROOT / 'Whatsapp'
EXPECTED_RESULT_ROOT = TEST_REPORT_ROOT / 'expected_results'
WHATSAPP_RESULT_ROOT = EXPECTED_RESULT_ROOT / 'Whatsapp'

test_builder = ToucanFileBuilder().with_expected_type("some type").add_rule("some rule", lambda a: True)
wa_db = test_builder.with_file_path(Path("wa.db")).build()
contacts_db = test_builder.with_file_path(Path("contacts.db")).build()
locations_db = test_builder.with_file_path(Path("locations.db")).build()

ALL_PASS_RESULTS = {
    wa_db: (True, {"has_messages": True, "has_pictures": True}),
    contacts_db: (True, {"has_contact_names": True, "has_phone_numbers": True})
}

SOME_FAIL_RESULTS = {
    wa_db: (False, {"has_messages": True, "has_pictures": False, "has_locations": False}),
    contacts_db: (True, {"has_contact_names": False, "has_phone_numbers": True}),
    locations_db: (False, {"has_location": True})
}

WHATSAPP_PASSED: ApplicationResult = ApplicationResult("Whatsapp", "2.0", ALL_PASS_RESULTS)
WHATSAPP_FAILED: ApplicationResult = ApplicationResult("Whatsapp", "2.0", SOME_FAIL_RESULTS)
WHATSAPP_NO_RESULTS: ApplicationResult = ApplicationResult.new_old_version("Whatsapp", "2.0")
WHATSAPP_NO_NEW_VERSION: ApplicationResult = ApplicationResult("Whatsapp")
WHATSAPP_ERROR: ApplicationResult = ApplicationResult.error("Whatsapp")
WHATSAPP_ERROR_WITH_NEW_VERSION: ApplicationResult = ApplicationResult.error("Whatsapp", "10.0")

TELEGRAM_PASSED: ApplicationResult = ApplicationResult("Telegram", "2.5", ALL_PASS_RESULTS)
TELEGRAM_FAILED: ApplicationResult = ApplicationResult("Telegram", "2.5", SOME_FAIL_RESULTS)
TELEGRAM_NO_RESULTS: ApplicationResult = ApplicationResult.new_old_version("Telegram", "2.5")
TELEGRAM_NO_NEW_VERSION: ApplicationResult = ApplicationResult("Telegram")

# An empty string should be treated just like a missing version
WHATSAPP_EMPTY_STRING_VERSION: ApplicationResult = ApplicationResult("Whatsapp", "")
TELEGRAM_EMPTY_STRING: ApplicationResult = ApplicationResult("Telegram", "")


class TestMarkdownReporter(unittest.TestCase):
    regenerate: bool = False

    @freeze_time("2024-10-02")
    def setUp(self):
        self.reporter = MarkdownReporter(report_root=TEST_REPORT_ROOT)

        self.test_general_readme = TEST_REPORT_ROOT / 'README.md'
        self.test_app_readme = WHATSAPP_REPORT_ROOT / 'README.md'
        self.test_app_readme_before = WHATSAPP_REPORT_ROOT / 'test_readme_before.md'
        self.test_previous_days = TEST_REPORT_ROOT / 'previous_days.csv'
        self.test_app_previous_days = WHATSAPP_REPORT_ROOT / 'previous_days.csv'

        self.test_files_before_after = {
            TEST_REPORT_ROOT / 'test_readme_before.md': self.test_general_readme,
            TEST_REPORT_ROOT / 'previous_days_before.csv': self.test_previous_days,
            self.test_app_readme_before: self.test_app_readme,
            WHATSAPP_REPORT_ROOT / 'previous_days_before.csv': self.test_app_previous_days
        }

    def test_regenerate_off(self):
        self.assertFalse(self.regenerate)

    @patch("toucan.reporter.markdown_reporter.git_checkout_and_pull")
    @patch.object(MarkdownReporter, '_push_reports')
    @patch.object(MarkdownReporter, '_application_report')
    @patch.object(MarkdownReporter, '_daily_summary')
    def test_without_git(self, daily_summary_mock, app_report_mock, push_mock, checkout_mock):
        app_results = [WHATSAPP_PASSED, TELEGRAM_FAILED]
        reporter_without_git = MarkdownReporter(report_root=TEST_REPORT_ROOT, git_pull_and_push=False)
        reporter_without_git.report_daily(app_results)

        daily_summary_mock.assert_called_once()
        self.assertEqual(len(app_results), app_report_mock.call_count)
        checkout_mock.assert_not_called()
        push_mock.assert_not_called()

    @patch("toucan.reporter.markdown_reporter.git_checkout_and_pull")
    @patch.object(MarkdownReporter, '_push_reports')
    @patch.object(MarkdownReporter, '_application_report')
    @patch.object(MarkdownReporter, '_daily_summary')
    def test_with_git(self, daily_summary_mock, app_report_mock, push_mock, checkout_mock):
        app_results = [WHATSAPP_PASSED, TELEGRAM_FAILED]
        reporter_with_git = MarkdownReporter(report_root=TEST_REPORT_ROOT, git_pull_and_push=True)
        reporter_with_git.report_daily(app_results)

        daily_summary_mock.assert_called_once()
        self.assertEqual(len(app_results), app_report_mock.call_count)
        checkout_mock.assert_called_once()
        checkout_mock.assert_called_with(TEST_REPORT_ROOT, 'master')
        push_mock.assert_called_once()
        push_mock.assert_called_with(TEST_REPORT_ROOT, 'README.md')

    def test_multiple_identical_apps(self):
        # writing a daily report with multiple results for the same app is not allowed
        with self.assertRaises(ValueError):
            self.reporter._daily_summary([WHATSAPP_PASSED, WHATSAPP_FAILED])
        with self.assertRaises(ValueError):
            self.reporter._daily_summary([TELEGRAM_PASSED, TELEGRAM_PASSED])

    def test_create_app_readme_from_template(self):
        readme_folder_path: Path = TEST_REPORT_ROOT / 'NonExistingApp'
        self.assertFalse(os.path.exists(readme_folder_path),
                         'Folder already exists. Manually remove the folder or run the finally block.')

        try:
            nonexisting_app_result: ApplicationResult = ApplicationResult("NonExistingApp")
            self.reporter._application_report(nonexisting_app_result)
            self.assertTrue(os.path.exists(readme_folder_path / 'README.md'))
        finally:
            shutil.rmtree(readme_folder_path)

    @parameterized.expand([
        ('pass.md', WHATSAPP_PASSED),
        ('fail.md', WHATSAPP_FAILED),
        ('no_results.md', WHATSAPP_NO_RESULTS),
        ('no_new_version.md', WHATSAPP_NO_NEW_VERSION),
        ('no_new_version_empty_string.md', WHATSAPP_EMPTY_STRING_VERSION),
        ('error.md', WHATSAPP_ERROR),
        ('error_with_new_version.md', WHATSAPP_ERROR_WITH_NEW_VERSION)
    ])
    def test_application_summary(self, expected_result, application_result: ApplicationResult):
        expected_result = EXPECTED_RESULT_ROOT / application_result.app_name / expected_result
        self.reporter._application_report(application_result)
        if self.regenerate:
            shutil.copyfile(self.test_app_readme, expected_result)
        else:
            with open(self.test_app_readme) as actual:
                with open(expected_result) as expected:
                    read = actual.read()
                    expected_read = expected.read()
                    self.assertEqual(read, expected_read)

    @parameterized.expand([
        ('all_pass.md', [WHATSAPP_PASSED, TELEGRAM_PASSED]),
        ('all_fail.md', [WHATSAPP_FAILED, TELEGRAM_FAILED]),
        ('one_fail.md', [WHATSAPP_PASSED, TELEGRAM_FAILED]),
        ('error_and_pass.md', [WHATSAPP_ERROR, TELEGRAM_PASSED]),
        ('error_with_new_version_and_pass.md', [WHATSAPP_ERROR_WITH_NEW_VERSION, TELEGRAM_PASSED]),
        ('error_and_no_result.md', [WHATSAPP_ERROR, TELEGRAM_NO_RESULTS]),
        ('error_and_failed.md', [WHATSAPP_ERROR, TELEGRAM_FAILED]),
        ('fail_and_no_results.md', [WHATSAPP_FAILED, TELEGRAM_NO_RESULTS]),
        ('pass_and_no_results.md', [WHATSAPP_PASSED, TELEGRAM_NO_RESULTS]),
        ('no_new_versions.md', [WHATSAPP_NO_NEW_VERSION, TELEGRAM_NO_NEW_VERSION]),
        ('no_new_versions_empty_strings.md', [WHATSAPP_EMPTY_STRING_VERSION, TELEGRAM_EMPTY_STRING]),
        ('no_applications.md', [])
    ])
    def test_daily_summary(self, expected_result, application_results):
        expected_result = EXPECTED_RESULT_ROOT / expected_result
        self.reporter._daily_summary(application_results)
        if self.regenerate:
            shutil.copyfile(self.test_general_readme, expected_result)
        else:
            with open(self.test_general_readme) as actual:
                with open(expected_result) as expected:
                    read = actual.read()
                    expected_read = expected.read()
                    self.assertEqual(read, expected_read)

    def test_previous_days_daily(self):
        expected_result = EXPECTED_RESULT_ROOT / "previous_days.csv"
        actual_path = self.test_previous_days
        application_results = [WHATSAPP_PASSED, TELEGRAM_FAILED]
        self.reporter._daily_summary(application_results)
        if self.regenerate:
            shutil.copyfile(actual_path, expected_result)
        with open(actual_path) as actual:
            with open(expected_result) as expected:
                read = actual.read()
                expected_read = expected.read()
        self.assertEqual(read, expected_read)

    def test_previous_days_application(self):
        expected_result = WHATSAPP_RESULT_ROOT / "previous_days.csv"
        actual_path = self.test_app_previous_days
        self.reporter._application_report(WHATSAPP_PASSED)
        if self.regenerate:
            shutil.copyfile(actual_path, expected_result)
        with open(actual_path) as actual:
            with open(expected_result) as expected:
                read = actual.read()
                expected_read = expected.read()
        self.assertEqual(read, expected_read)

    def tearDown(self):
        # return the test readme files to their former state
        for before, after in self.test_files_before_after.items():
            self.return_readmes_to_former_state(before, after)

        with open(self.test_app_readme_before, 'r') as old_file:
            old_content = old_file.read()

        with open(self.test_app_readme, 'w') as current_file:
            current_file.write(old_content)

    def return_readmes_to_former_state(self, test_readme_before: str, test_readme: str):
        with open(test_readme_before, 'r') as old_file:
            old_content = old_file.read()

        with open(test_readme, 'w') as current_file:
            current_file.write(old_content)


if __name__ == '__main__':
    unittest.main()
