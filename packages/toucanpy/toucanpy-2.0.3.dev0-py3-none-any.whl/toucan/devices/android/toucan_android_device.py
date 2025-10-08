from dataclasses import dataclass
from time import sleep

from adb_pywrapper.adb_device import AdbDevice
from adb_pywrapper.adb_result import AdbResult

from toucan.devices import logger
from toucan.devices.android.emulator import AndroidEmulator
from toucan.devices.base_emulator import BaseEmulator


POLL_WAIT_TIME = 1
BOOT_PROP = 'dev.bootcomplete'


@dataclass
class AvdDevice:
    avd_device_name: str
    adb_name: str
    status: str


class ToucanAndroidDevice(BaseEmulator):
    """
    A class to use Android emulators in Toucan.
    This class implements all methods from BaseEmulator by calling emulator.py and adb_pywrapper code.
    """

    def __init__(self, avd_name: str, max_wait_time: int, interactive: bool = False) -> None:
        self.avd_device_name: str = avd_name
        self.emulator: AndroidEmulator = AndroidEmulator(interactive=interactive, avd_device_name=self.avd_device_name)
        self.adb_device: AdbDevice = None
        self.is_started = False
        self.max_wait_time = max_wait_time

    def _check_if_device_is_already_started(self) -> AdbDevice | None:
        for adb_name in AdbDevice.list_devices():
            emu_avd_name_result = AdbDevice(adb_name).emulator_emu_avd('name')
            if emu_avd_name_result.success and emu_avd_name_result.stdout:
                result = AvdDevice(
                    emu_avd_name_result.stdout.splitlines()[0], adb_name, AdbDevice.get_device_status(adb_name)
                )

                if result.avd_device_name == self.avd_device_name:
                    logger.info(f'{self.avd_device_name} was found successfully')

                    return AdbDevice(adb_name)

        return None

    def _wait_until_avd_is_available_on_adb(self) -> AdbDevice | None:
        total_wait_time = 0

        device = None
        while total_wait_time < self.max_wait_time and device is None:
            sleep(POLL_WAIT_TIME)
            total_wait_time += POLL_WAIT_TIME
            device = self._check_if_device_is_already_started()

        return device

    def start_emulator(self, snapshot: str = None, log=True) -> AdbDevice:
        """
        Should only return if the device is available for use in Toucan. For Android devices, this means that:
        - the device has to be booted
        - an adb connection has been made
        - root access is gained
        """

        # if already booted: shutdown over adb
        if self._check_if_device_is_already_started():
            logger.info(
                f'{self.avd_device_name} was already booted, shutting down because we need to control the process'
            )
            self._check_if_device_is_already_started().shell('reboot -p')
            logger.info(f'Waiting for 15 seconds for {self.avd_device_name} to shut down')
            sleep(15)

        self.emulator.start_emulator(snapshot=snapshot)

        # wait until emulator is available on ADB
        self.adb_device = self._wait_until_avd_is_available_on_adb()
        if self.adb_device is None:
            raise Exception(f'could not connect to emulator {self.avd_device_name} over adb')

        total_wait_time = 0
        while total_wait_time < self.max_wait_time:
            sleep(POLL_WAIT_TIME)
            total_wait_time += POLL_WAIT_TIME

            if self.adb_device.get_prop(BOOT_PROP) == '1\n':
                self.is_started = True
                logger.info(f'Device {self.avd_device_name} is booted completely')
                break

        if not self.is_started:
            raise Exception(
                f'Device {self.avd_device_name} is available over adb but cannot fully boot. '
                f'Adb name: {self.adb_device.device}'
            )

        got_root = False
        for i in range(5):
            if self.adb_device.root().success:
                got_root = True
                break
            sleep(1)
        if not got_root:
            raise Exception(f'Could not get root access on {self.adb_device.device}')

        return self.adb_device

    def shutdown_emulator(self):
        self.emulator.shutdown_emulator()
        self.adb_device = None
        self.is_started = False

    def snapshots_list(self, snapshot_prefix: str | None) -> list[str]:
        """
        Get the names of all available snapshots.

        :param snapshot_prefix: The prescribed format for a snapshot name, e.g. "toucan_run_"
        :return: a list of names of all available snapshots.
        """
        all_snapshots = self.adb_device.emulator_snapshots_list()

        if snapshot_prefix:
            return [snap for snap in all_snapshots if snapshot_prefix in snap]
        else:
            return all_snapshots

    def snapshot_delete(self, delete: list[str] = None) -> AdbResult:
        """
        Delete snapshots based on a list.
        If some but not all provided snapshots are removed success will be False, and a list of invalid snapshots
        is passed as a stderr.
        :param delete: a list containing snapshot names (str) to be deleted. Example: ['snap_name_1','snap_name_3']
        :return: AdbResult object with stdout, stderr if applicable and success True/False
        """
        return self.adb_device.emulator_snapshot_delete(delete)

    def snapshot_save(self, snapshot_name: str) -> AdbResult:
        """
        Create a snapshot of the current state of the emulator.
        :param snapshot_name: The name of the snapshot.
        :return: AdbResult object with stdout, stderr if applicable and success True/False.
        """
        if snapshot_name in self.adb_device.emulator_snapshots_list():
            logger.info(f'Deleting old snapshot {snapshot_name}')
            self.adb_device.emulator_snapshot_delete([snapshot_name])
        return self.adb_device.emulator_snapshot_save(snapshot_name)

    def snapshot_load(self, snapshot_name: str) -> AdbResult:
        """
        Load a snapshot of the emulator.
        :param snapshot_name: The name of the snapshot.
        :return: AdbResult object with stdout, stderr if applicable and success True/False.
        """
        return self.adb_device.emulator_snapshot_load(snapshot_name)

    def install(self, installation_file: str, r: bool = False) -> AdbResult:
        return self.adb_device.install(installation_file, r)

    def snapshot_revert_to_latest_successful(self):
        super().snapshot_revert_to_latest_successful()

    def snapshot_run_successful(self, debug_mode: bool = False):
        super().snapshot_run_successful(debug_mode)
