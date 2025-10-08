import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from test.resources.config import TOUCAN_CONFIG
from toucan.devices.emulator_service import EmulatorService, start_emulators, update_app, get_file_from_emulator
from toucan.runner import ToucanConfig


def mock_apk_app_name(apk_path):
    return "dummy"


def mock_get_apk_version(apk_path):
    return "1.2.3"


def mock_get_apk_package_name(apk_path):
    return "com.dummy"


def mock_basename(file_path):
    return 'file1.db'


class TestEmulatorService(unittest.TestCase):
    def setUp(self):
        config = ToucanConfig(
            alice=TOUCAN_CONFIG['emulators']['alice'],
            bob=TOUCAN_CONFIG['emulators']['bob'],
            use_snapshots=TOUCAN_CONFIG['emulators']['use_snapshots'],
            debug_snapshot_name=TOUCAN_CONFIG['emulators']['debug_snapshot_name'],
            wait_time=TOUCAN_CONFIG['emulators']['wait_time']
        )
        self.emulator_service = EmulatorService(config)

    @patch.object(EmulatorService, "get_emulator_alice")
    @patch.object(EmulatorService, "get_emulator_bob")
    def test_start_emulators(self, mock_get_bob, mock_get_alice):
        mock_get_bob.return_value = Mock()
        mock_get_alice.return_value = Mock()
        alice, bob = start_emulators(TOUCAN_CONFIG)
        # TODO check alice and bob individually
        alice.start_emulator.assert_called_once()
        bob.start_emulator.assert_called_once()

    @patch('toucan.devices.emulator_service.get_apk_app_name', mock_apk_app_name)
    @patch('toucan.devices.emulator_service.get_apk_package_name', mock_get_apk_package_name)
    @patch('toucan.devices.emulator_service.get_installed_app_version', side_effect=['1.2.2', '1.2.3'])
    @patch('toucan.devices.emulator_service.get_apk_version', mock_get_apk_version)
    def test_update_app_newer_version(self, get_installed_app_version):
        emulator = Mock(install=Mock(result_value=Mock()))
        result = update_app(Path('apk_path'), emulator)
        self.assertTrue(result)

    @patch('toucan.devices.emulator_service.get_apk_app_name', mock_apk_app_name)
    @patch('toucan.devices.emulator_service.get_apk_package_name', mock_get_apk_package_name)
    @patch('toucan.devices.emulator_service.get_installed_app_version', side_effect=['1.2.2', '1.2.2'])
    @patch('toucan.devices.emulator_service.get_apk_version', mock_get_apk_version)
    def test_update_app_fails(self, get_installed_app_version):
        emulator = Mock(install=Mock(result_value=Mock()))
        result = update_app(Path('apk_path'), emulator)
        self.assertFalse(result)

    @patch('toucan.devices.emulator_service.os.rename')
    @patch('toucan.devices.emulator_service.basename', mock_basename)
    def test_get_file_from_emulator(self, mock_rename):
        adb_device = Mock()

        alice = Mock()
        alice.adb_device = adb_device

        toucan_file = Mock()
        toucan_file.file_path.return_value = Path('/some/file1.db')
        toucan_file.pull.return_value = Path('some/folder/file1.db')

        new_file_path = get_file_from_emulator(alice, toucan_file, "some/folder", "dummy_app", "1.2.3")
        self.assertEqual(new_file_path, Path('some/folder/Toucan_dummy_app_v1.2.3_file1.db'))

        toucan_file.pull.assert_called()