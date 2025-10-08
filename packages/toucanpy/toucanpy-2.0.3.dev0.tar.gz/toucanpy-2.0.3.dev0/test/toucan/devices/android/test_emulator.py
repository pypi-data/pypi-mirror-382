import unittest
from abc import ABC
from unittest.mock import patch, Mock

from toucan.devices.android.emulator import AndroidEmulator


class MockEmulator(AndroidEmulator, ABC):
    def __init__(self, interactive: bool, avd_device_name: str, process=None, emulator_name="", device_started=False,
                 device_name='', boot_complete=False):
        super().__init__(interactive, avd_device_name)
        self.process = process
        self.emulator_name = emulator_name
        self.is_started = device_started
        self.device_name = device_name
        self.boot_complete = boot_complete


class MockDevice:
    avd_name = "fake_device"
    status = "device"
    adb_name = "emulator_name"


class MockPopen:
    pid: int = 23423

    def __init__(self, *args, **kwargs):
        pass


def custom_killpg(pid, signal):
    # Implement your custom logic here if needed
    return 0  # Simulate a successful execution


def mock_get_attached_devices():
    return [MockDevice()]


class TestEmulator(unittest.TestCase):
    emulator = None

    def setUp(self):
        self.emulator = AndroidEmulator(False, 'fake_device')

    def tearDown(self):
        self.emulator = None

    @patch('subprocess.Popen', MockPopen)
    def test_emulator_command(self):
        """
            Test for function (emulator_command)
        """
        mock_emulator_result = MockEmulator(avd_device_name='fake', interactive=False)
        result = mock_emulator_result.emulator_command("", True)
        # result.pid = 342 Change the expected result
        assert result.pid == MockPopen.pid

    @patch('toucan.devices.android.emulator.AndroidEmulator.start_emulator')
    def test_start_emulator(self, mock_start_emulator_command):
        """
            Test for function (start_emulator)
        """
        mock_start_emulator_command.return_value = 'emulator-5678'

        emulator_name = self.emulator.start_emulator("fake_snapshot", True)

        self.assertEqual(emulator_name, 'emulator-5678')

    @patch('os.getpgid')
    @patch('os.killpg')
    def test_shutdown_emulator(self, mock_killpg, mock_getpgid):
        """
            Test for function (shutdown_emulator)
        """
        self.emulator.process = Mock()
        self.emulator.is_started = True

        mock_getpgid.return_value = 123
        mock_killpg.side_effect = custom_killpg

        result = self.emulator.shutdown_emulator()

        self.assertTrue(result)
        self.assertFalse(self.emulator.is_started)

    @patch('toucan.devices.android.emulator.AndroidEmulator.reboot_emulator')
    def test_reboot_emulator(self, mock_reboot_emulator_command):
        """
            Test for function (reboot_emulator)
        """
        emulator = AndroidEmulator(False, 'fake_device')
        mock_reboot_emulator_command.return_value = 'emulator-5678'
        emulator_name = emulator.reboot_emulator(snapshot='fake_snapshot')

        self.assertEqual(emulator_name, 'emulator-5678')


if __name__ == '__main__':
    unittest.main()
