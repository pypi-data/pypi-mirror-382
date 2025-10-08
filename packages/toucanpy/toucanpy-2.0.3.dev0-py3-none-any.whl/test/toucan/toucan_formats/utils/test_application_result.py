import textwrap
import unittest
from pathlib import Path

from toucan.formats.format import ToucanFileBuilder
from toucan.reporter.application_result import ApplicationResult, Status, pretty_print

test_builder = ToucanFileBuilder().with_expected_type("some type").add_rule("some rule", lambda a: True)
wa_db = test_builder.with_file_path(Path("wa.db")).build()
contacts_db = test_builder.with_file_path(Path("contacts.db")).build()

ALL_PASS_RESULTS = {
    wa_db: (True, {"has_messages": True, "has_pictures": True}),
    contacts_db: (True, {"has_contact_names": True, "has_phone_numbers": True})
}

SOME_FAIL_RESULTS = {
    wa_db: (False, {"has_messages": True, "has_pictures": False}),
    contacts_db: (True, {"has_contact_names": False, "has_phone_numbers": True})
}


class TestApplicationResult(unittest.TestCase):

    def test_constructor(self):
        result = ApplicationResult("Whatsapp")
        self.assertEqual("Whatsapp", result.app_name)
        self.assertIsNone(result.new_version)
        self.assertIsNone(result.results)

        result = ApplicationResult("Whatsapp", "2.0", run_status=Status.ERROR)
        self.assertEqual("Whatsapp", result.app_name)
        self.assertEqual("2.0", result.new_version)
        self.assertIsNone(result.results)

        result = ApplicationResult("Whatsapp", "2.0", ALL_PASS_RESULTS)
        self.assertEqual("Whatsapp", result.app_name)
        self.assertEqual("2.0", result.new_version)
        self.assertEqual(ALL_PASS_RESULTS, result.results)

        result = ApplicationResult.error("Whatsapp", "2.0")
        self.assertEqual("Whatsapp", result.app_name)
        self.assertEqual("2.0", result.new_version)
        self.assertFalse(result.has_results())
        self.assertEqual(Status.ERROR, result.run_status)

        result = ApplicationResult.new_old_version("Whatsapp", "2.0")
        self.assertEqual("Whatsapp", result.app_name)
        self.assertEqual("2.0", result.new_version)
        self.assertFalse(result.has_results())
        self.assertEqual(Status.NEW_OLD_VERSION, result.run_status)

        with (self.assertRaises(TypeError)):
            ApplicationResult()  # missing app name
        with (self.assertRaises(ValueError)):
            ApplicationResult(app_name=None)
        with (self.assertRaises(ValueError)):
            ApplicationResult(app_name="")
        with (self.assertRaises(ValueError)):
            ApplicationResult("Whatsapp", results=ALL_PASS_RESULTS)  # results without version number
        # success with new version but without results is not allowed
        with (self.assertRaises(ValueError)):
            ApplicationResult("Whatsapp", "2.0", {}, run_status=Status.SUCCESS)
        with (self.assertRaises(ValueError)):
            ApplicationResult("Whatsapp", new_version="2.0", run_status=Status.SUCCESS)

    def test_has_new_version(self):
        result = ApplicationResult("Whatsapp")
        self.assertFalse(result.has_new_version())
        result = ApplicationResult.new_old_version("Whatsapp", "2.0")
        self.assertTrue(result.has_new_version())
        # an empty string is treated as no new version
        result = ApplicationResult("Whatsapp", "")
        self.assertFalse(result.has_new_version())

    def test_has_result(self):
        result = ApplicationResult("Whatsapp")
        self.assertFalse(result.has_results())
        result = ApplicationResult.new_old_version("Whatsapp", "2.0")
        self.assertFalse(result.has_results())
        result = ApplicationResult("Whatsapp", "2.0", ALL_PASS_RESULTS)
        self.assertTrue(result.has_results())

    def test_analysis_all_pass(self):
        result = ApplicationResult("Whatsapp", "2.0", ALL_PASS_RESULTS)
        self.assertTrue(result.has_complete_support())
        self.assertTrue(result.all_files_recognized())
        self.assertTrue(result.all_parsing_rules_pass())
        self.assertListEqual([], result.all_unrecognized_files())
        self.assertDictEqual({}, result.all_failed_rules())

    def test_analysis_some_failures(self):
        result = ApplicationResult("Whatsapp", "2.0", SOME_FAIL_RESULTS)
        self.assertFalse(result.has_complete_support())
        self.assertFalse(result.all_files_recognized())
        self.assertFalse(result.all_parsing_rules_pass())
        self.assertListEqual([wa_db], result.all_unrecognized_files())
        self.assertDictEqual({wa_db: ['has_pictures'], contacts_db: ['has_contact_names']},
                             result.all_failed_rules())

    def test_analysis_no_results(self):
        result = ApplicationResult("Whatsapp")  # no new version
        self.assertIsNone(result.has_complete_support())
        self.assertIsNone(result.all_files_recognized())
        self.assertIsNone(result.all_parsing_rules_pass())
        self.assertListEqual([], result.all_unrecognized_files())
        self.assertDictEqual({}, result.all_failed_rules())

    # TODO TOUCAN-246: move
    def test_pretty_print(self):
        results = [ApplicationResult("Whatsapp", "2.0", SOME_FAIL_RESULTS),
                   ApplicationResult("Telegram", "3.0", ALL_PASS_RESULTS),
                   ApplicationResult.new_old_version("Instagram", "1.5"),  # old new version
                   ApplicationResult.error("Instagram", "10.0"),  # run error
                   ApplicationResult("Snapchat")  # no new version
                   ]
        expected_string = """
                Whatsapp v2.0 - Run status: Status.SUCCESS
                ==========================================
                wa.db
                \tRecognition: FAILED
                \thas_messages: ok
                \thas_pictures: FAILED
                contacts.db
                \tRecognition: ok
                \thas_contact_names: FAILED
                \thas_phone_numbers: ok
                Telegram v3.0 - Run status: Status.SUCCESS
                ==========================================
                wa.db
                \tRecognition: ok
                \thas_messages: ok
                \thas_pictures: ok
                contacts.db
                \tRecognition: ok
                \thas_contact_names: ok
                \thas_phone_numbers: ok
                Instagram v1.5 - Run status: Status.NEW_OLD_VERSION
                ===================================================
                -no results-
                Instagram v10.0 - Run status: Status.ERROR
                ==========================================
                -no results-
                Snapchat - no new version - Run status: Status.SUCCESS
                ======================================================
                -no results-
                """
        # remove indentation and newline at start and end of the string above
        expected_string = textwrap.dedent(expected_string)[1:-1]
        self.assertEqual(expected_string, pretty_print(results))


if __name__ == '__main__':
    unittest.main()
