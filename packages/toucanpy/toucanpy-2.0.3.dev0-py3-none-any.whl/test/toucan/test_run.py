import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from test.resources.config import TOUCAN_CONFIG
from toucan.reporter.application_result import ApplicationResult
from toucan.config import ToucanConfig
from toucan.formats.format import ToucanFormat, ToucanFileBuilder
from toucan.runner import ToucanRunner


class DummyFormat(ToucanFormat):

    def __init__(self):
        super().__init__(app_name='dummy', package_name='com.dummy', toucan_files=[
            Mock(filepath='/some/file1.db'),
            Mock(filepath='/some/file2.db')
        ])
        self.execute_actions_called = 0

    def get_latest_version(self) -> str:
        return "1.2.3"

    def get_latest_apk(self, store_path: Path):
        pass

    def execute_actions(self, alice: str, bob: str):
        self.execute_actions_called = self.execute_actions_called + 1

    def recognize_file(self, path_to_file: Path) -> str:
        return '{"recognize" : "dummy"}'

    def parse_file(self, path_to_file: Path) -> str:
        return '{"parse" : "dummy"}'


def mock_apk_app_name(apk_path):
    return "dummy"


def mock_get_apk_version(apk_path):
    return "1.2.3"


def mock_get_apk_package_name(apk_path):
    return "com.dummy"


def mock_basename(file_path):
    return 'file1.db'


def mock_emulator_service(self, interactive):
    self.get_emulator_alice = Mock(start_emulator=Mock())
    self.get_emulator_bob = Mock(start_emulator=Mock())


class TestRunScript(unittest.TestCase):
    def setUp(self):
        self.dummy_format = DummyFormat()
        self.mock_reporter = Mock()
        self.mock_reporter.report_root = Path('')
        config = ToucanConfig(
            alice=TOUCAN_CONFIG['emulators']['alice'],
            bob=TOUCAN_CONFIG['emulators']['bob'],
            use_snapshots=TOUCAN_CONFIG['emulators']['use_snapshots'],
            debug_snapshot_name=TOUCAN_CONFIG['emulators']['debug_snapshot_name'],
            wait_time=TOUCAN_CONFIG['emulators']['wait_time']
        )
        self.runner = ToucanRunner([self.dummy_format], self.mock_reporter, config)
        self.mock_alice = Mock(adb_device=Mock(device="alice_adb"))
        self.mock_bob = Mock(adb_device=Mock(device="bob_adb"))

        self.test_builder = ToucanFileBuilder().with_expected_type("some type").add_rule("some rule", lambda a: True)
        self.wa_db = self.test_builder.with_file_path(Path("/test/wa.db")).build()
        self.contacts_db = self.test_builder.with_file_path(Path("/bla/contacts.db")).build()

        self.all_pass_results = {
            self.wa_db: (True, {"has_messages": True, "has_pictures": True}),
            self.contacts_db: (True, {"has_contact_names": True, "has_phone_numbers": True})
        }
        self.some_fail_results = {
            self.wa_db: (False, {"has_messages": True, "has_pictures": False}),
            self.contacts_db: (True, {"has_contact_names": False, "has_phone_numbers": True})
        }

        # Patch multiple instance variables
        self.patches = [
            patch.object(self.runner, "current_version", "1.1.1"),
            patch.object(self.runner, "alice", self.mock_alice),
            patch.object(self.runner, "bob", self.mock_bob),
        ]

        # Start all patches
        self.mocks = [p.start() for p in self.patches]

    def tearDown(self):
        for p in self.patches:
            p.stop()

    @patch('toucan.runner.versions.is_newer_version')
    @patch('toucan.runner.update_app')
    @patch('toucan.runner.get_file_from_emulator',
           side_effect=[Path('some/folder/Toucan_dummy_app_v1.2.3_file1.db'),
                        Path('some/folder/Toucan_dummy_app_v1.2.3_file2.db')])
    @patch('toucan.runner.get_installed_app_version')
    @patch.object(ToucanRunner, '_store_support')
    def test_run_toucan_format(self, store_support, get_installed_version, file_from_emulator,
                               update_app, new_version):
        result = self.runner.run_toucan_format(self.dummy_format)

        self.assertEqual(result.app_name, "dummy")
        self.assertEqual(result.new_version, "1.2.3")

        self.assertEqual(len(result.results), 2)

        self.assertEqual(1, self.dummy_format.execute_actions_called, "Expected execute_actions to be called exactly once!")

    @patch('toucan.runner.get_file_from_emulator')
    @patch.object(ToucanRunner, '_store_results')
    def test_get_file_results(self, mock_store_results, mock_get_file):
        mock_get_file.return_value = Path('mocked_file')

        file_results = {}
        self.runner._get_file_results(self.dummy_format, file_results)

        self.dummy_format.toucan_files[0].verify_type.assert_called_with(self.dummy_format.recognize_file(Path('dummy')))
        self.dummy_format.toucan_files[0].verify_parsed_result.assert_called_with(self.dummy_format.parse_file(Path('dummy')))
        self.dummy_format.toucan_files[1].verify_type.assert_called_with(self.dummy_format.recognize_file(Path('dummy')))
        self.dummy_format.toucan_files[1].verify_parsed_result.assert_called_with(self.dummy_format.parse_file(Path('dummy')))

    @patch('toucan.runner.get_installed_app_version')
    @patch('toucan.runner.logger')
    def test_run_toucan_format_error_occurs(self, logger, get_installed_app_version):
        # make an internal call from run_toucan_format raise an exception
        get_installed_app_version.side_effect = Exception('Some error')

        result = self.runner.run_toucan_format(self.dummy_format)

        logger.error.assert_called_once_with(
            f"Something went wrong while running Toucan for application {self.dummy_format.app_name}: Some error",
            exc_info=True)
        self.assertEqual('ERROR', result.run_status.name)
        self.mock_alice.snapshot_save.assert_called_once()
        self.mock_bob.snapshot_save.assert_called_once()

        self.mock_alice.snapshot_load.assert_called_once()
        self.mock_bob.snapshot_load.assert_called_once()

    @patch.object(ToucanRunner, 'run_toucan_format')
    @patch('toucan.runner.start_emulators')
    def test_daily_report(self, mock_start_emulators, mock_run_toucan_format):
        my_mock_result = Mock()

        mock_start_emulators.return_value = (self.mock_alice, self.mock_bob)
        mock_run_toucan_format.return_value = my_mock_result

        self.runner.run()

        self.mock_reporter.report_results.assert_called_with([my_mock_result])
        # Ensure both emulators are shut down
        self.mock_alice.shutdown_emulator.assert_called_once()
        self.mock_bob.shutdown_emulator.assert_called_once()

    @patch('toucan.runner.get_installed_app_version')
    @patch('toucan.runner.get_file_from_emulator',
           side_effect=[Path('some/folder/Toucan_dummy_app_v1.2.3_file1.db'),
                        Path('some/folder/Toucan_dummy_app_v1.2.3_file2.db')])
    @patch('toucan.runner.update_app')
    @patch.object(ToucanRunner, '_store_support')
    @patch.object(ToucanRunner, '_version_supported')
    @patch('toucan.runner.start_emulators')
    def test_run_toucan_format_no_newer_version(self, emulators, version_supported, store_support,
                                                update_app,
                                                file_from_emulator, get_installed_app_version):
        emulators.return_value = (self.mock_alice, self.mock_bob)

        # if the current version is the same as the newest version and the previous run was successful, an empty result is expected
        get_installed_app_version.return_value = "1.2.3"
        version_supported.return_value = True
        result_same_version_success = self.runner.run_toucan_format(self.dummy_format)
        self.assertEqual(ApplicationResult(self.dummy_format.app_name).run_status.name,result_same_version_success.run_status.name)

        # if the current version is the same as the newest version and the previous run was not successful, another run is expected
        get_installed_app_version.return_value = "1.2.3"
        version_supported.return_value = False
        result_same_version = self.runner.run_toucan_format(self.dummy_format)

        self.assertEqual(result_same_version.app_name, "dummy")
        self.assertEqual(result_same_version.new_version, "1.2.3")
        self.assertEqual(len(result_same_version.results), 2)

        # if the current version is higher than the newest version, a specific result is expected
        get_installed_app_version.return_value = "2.0"
        result_same_version = self.runner.run_toucan_format(self.dummy_format)
        self.assertEqual(ApplicationResult.new_old_version(self.dummy_format.app_name, "1.2.3").run_status.name, result_same_version.run_status.name)

    @patch('toucan.runner.open')
    def test_store_support(self, open_patch):
        file_results = {}
        self.runner._store_support(DummyFormat(), file_results)
        open_patch.assert_called_once()

    @patch('toucan.runner.open')
    def test_store_support_no_support(self, open_patch):
        self.runner._store_support(DummyFormat(), self.some_fail_results)
        open_patch.assert_not_called()

    @patch('os.listdir')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    def test_previous_run_supported(self, os_exists, os_isdir, os_listdir):
        os_exists.return_value = True
        os_listdir.return_value = ['dummy_name_supported.txt']
        self.assertTrue(self.runner._version_supported('dummy_name'))

    @patch('os.listdir')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    def test_previous_run_unsupported(self, os_exists, os_isdir, os_listdir):
        os_exists.return_value = True
        os_listdir.return_value = ['dummy_name_unsupported.txt']
        self.assertFalse(self.runner._version_supported('dummy_name'))

    @patch('os.listdir')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    def test_no_previous_run(self, os_exists, os_isdir, os_listdir):
        os_exists.return_value = False
        os_listdir.return_value = ['dummy_name_supported.txt']
        self.assertFalse(self.runner._version_supported('dummy_name'))

    def test_toucan_config(self):
        with self.assertRaises(ValueError) as context:
            ToucanConfig(
                None, None, None, None, None
            )
        self.assertEqual(str(context.exception), 'alice should be present and filled in the config file.')

        with self.assertRaises(ValueError) as context:
            ToucanConfig(
                'alice', None, None, None, None
            )
        self.assertEqual(str(context.exception), 'bob should be present and filled in the config file.')

        with self.assertRaises(ValueError) as context:
            ToucanConfig(
                'alice', 'bob', None, None, None
            )
        self.assertEqual(str(context.exception), 'use_snapshots should be present and filled in the config file.')

        with self.assertRaises(ValueError) as context:
            ToucanConfig(
                'alice', 'bob', True, None, None
            )
        self.assertEqual(str(context.exception), 'debug_snapshot_name should be present and filled in the config file.')

        with self.assertRaises(ValueError) as context:
            ToucanConfig(
                'alice', 'bob', True, 'debug', None
            )
        self.assertEqual(str(context.exception), 'wait_time should be present and filled in the config file.')

        config = ToucanConfig(
            'alice', 'bob', True, 'debug', 60
        )

        self.assertEqual(config.alice, 'alice')
        self.assertEqual(config.bob, 'bob')
        self.assertEqual(config.use_snapshots, True)
        self.assertEqual(config.debug_snapshot_name, 'debug')
        self.assertEqual(config.wait_time, 60)


if __name__ == '__main__':
    unittest.main()
