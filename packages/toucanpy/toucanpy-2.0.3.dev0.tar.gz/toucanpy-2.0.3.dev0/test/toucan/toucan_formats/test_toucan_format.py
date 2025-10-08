import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import Mock, patch

from toucan.formats.format import ToucanFileBuilder


def mock_basename(file_path):
    return 'my.db'


class TestToucanFile(unittest.TestCase):

    def setUp(self):
        builder = ToucanFileBuilder().with_file_path(Path("/some/file/on/phone.jpg")).with_expected_type("jpeg")
        builder.add_rule("contains a", lambda parsing_result: 'a' in parsing_result)
        builder.add_rule("contains b", lambda parsing_result: 'b' in parsing_result)
        builder.add_rule("contains c", lambda parsing_result: 'c' in parsing_result)
        self.toucan_file = builder.build()

    def test_builder_missing_arguments(self):
        # missing file path
        with self.assertRaises(ValueError):
            ToucanFileBuilder().with_expected_type("sqlite3").add_rule("a", lambda a: True).build()
        # missing type
        with (self.assertRaises(ValueError)):
            ToucanFileBuilder().with_file_path(Path("/data/something.db")).add_rule(
                "a", lambda a: True).build()
        # missing rules
        with self.assertRaises(ValueError):
            ToucanFileBuilder().with_file_path(Path("/data/something.db")).with_expected_type("sqlite3").build()

    def test_duplicate_rules(self):
        builder = ToucanFileBuilder().with_file_path(Path("/some/file/on/phone.jpg")).with_expected_type("jpeg")
        builder.add_rule("contains a", lambda parsing_result: 'a' in str(parsing_result))
        with self.assertRaises(ValueError):
            builder.add_rule("contains a", lambda parsing_result: 'a' in str(parsing_result))

    def test_immutables(self):
        with self.assertRaises(FrozenInstanceError):
            self.toucan_file.file_path = "a"
        with self.assertRaises(FrozenInstanceError):
            self.toucan_file.expected_type = "a"
        with self.assertRaises(FrozenInstanceError):
            self.toucan_file.parsing_rules = {}
        with self.assertRaises(TypeError):
            self.toucan_file.parsing_rules["new rule"] = lambda a: False

    def test_file_type_verification(self):
        self.assertTrue(self.toucan_file.verify_type("jpeg"))
        self.assertFalse(self.toucan_file.verify_type("Jpeg"))
        self.assertFalse(self.toucan_file.verify_type(".jpeg"))
        self.assertFalse(self.toucan_file.verify_type(".png"))
        self.assertFalse(self.toucan_file.verify_type(""))
        self.assertFalse(self.toucan_file.verify_type(None))
        self.assertFalse(self.toucan_file.verify_type(1))

    def test_parsing_validation(self):
        all_pass = self.toucan_file.verify_parsed_result("abc")
        self.assertDictEqual({"contains a": True, "contains b": True, "contains c": True}, all_pass)

        some_fail = self.toucan_file.verify_parsed_result("cdef")
        self.assertDictEqual({"contains a": False, "contains b": False, "contains c": True}, some_fail)

        all_fail = self.toucan_file.verify_parsed_result("hijklmnop")
        self.assertDictEqual({"contains a": False, "contains b": False, "contains c": False}, all_fail)

    def test_pull_single(self):
        adb_device = Mock()

        output_path = self.toucan_file.pull(adb_device, 'some/folder')

        self.assertEqual(str(output_path), 'some/folder/phone.jpg')
        adb_device.pull.assert_called_with('/some/file/on/phone.jpg', 'some/folder')

    @patch('toucan.formats.format.Path.mkdir')
    @patch('toucan.formats.format.subprocess.run')
    @patch('toucan.formats.format.basename', mock_basename)
    def test_sqlite_pull_multi(self, subprocess_run, mkdir):
        adb_device = Mock()
        adb_device.ls.return_value = ['/some/file/on/my.db', '/some/file/on/my.db-wal']
        adb_device.pull_multi.return_value = [Mock(success=True), Mock(success=True)]

        builder = ToucanFileBuilder().with_file_path(Path("/some/file/on/my.db")).with_expected_type("SQLite 3")
        builder.add_rule("contains a", lambda parsing_result: 'a' in parsing_result)
        builder.is_sqlite()

        sqlite_file = builder.build()

        output_path = sqlite_file.pull(adb_device, 'some/folder')

        self.assertEqual(str(output_path), 'some/folder/my.db')
        adb_device.pull_multi.assert_called_with(['/some/file/on/my.db', '/some/file/on/my.db-wal'], 'some/folder')
        subprocess_run.assert_called_with(['sqlite3', 'some/folder/my.db', 'VACUUM;'])


if __name__ == '__main__':
    unittest.main()
