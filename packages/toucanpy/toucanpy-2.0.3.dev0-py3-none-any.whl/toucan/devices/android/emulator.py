import os
import signal
import subprocess
from time import sleep

from toucan.devices.android import logger
from toucan.utils import ANDROID_SDK_HOME, RESULTS_ROOT
from toucan.utils.time_utils import get_current_time


EMULATOR: str = f'{ANDROID_SDK_HOME}/emulator/emulator'
LOG_FOLDER = f'{RESULTS_ROOT}/log'


def get_devices() -> list[str]:
    """
    Gets the list of devices available to the Android emulator.
    :return: a list of device names
    """
    logger.info('Looking for existing devices...')
    devices = subprocess.getoutput(f'{EMULATOR} -list-avds').splitlines()  # noqa: S605
    logger.info(f'{len(devices)} devices found: {devices}')
    return devices


def pick_first_available_device() -> str | None:
    """
    Gets the list of Android devices from the emulator, and returns the first one.
    If no device is available, an error is thrown and the program terminates.
    :return: The first devices listed by `emulator -list-avds`
    """
    devices = get_devices()
    if not devices:
        logger.error('No device found, set up a device before running this code!')
        return None
    if len(devices) > 1:
        logger.info('Multiple devices found, defaulting to first device')
    logger.info(f'Device chosen: {devices[0]}')
    return devices[0]


def _check_device_name(device_name: str) -> str | None:
    """
    Checks the given avd_device_name argument from start_device().
    If the argument is None, this method returns the first available device listed by `emulator -list-avds`.
    If the argument is a device name not listed by `emulator -list-avds`, an error is logged and the program terminates.
    :param device_name: device name to check
    :return: the avd_device_name to use
    """
    if device_name is None:
        logger.error('No device specified, picking first device available')
        return pick_first_available_device()
    if device_name not in get_devices():
        logger.error(f'Device {device_name} not found, check name or set up this device first')
    return device_name


def _get_log_file_path() -> str:
    """
    Generates the path for a new log file.
    The file has the name 'log/emulator_<TIMESTAMP>.log'
    :return: formats the path for a new logfile to use
    """
    os.makedirs(LOG_FOLDER, exist_ok=True)
    timestamp = get_current_time()
    return f'{LOG_FOLDER}/emulator_{timestamp}.log'


class AndroidEmulator:
    """
    Manages the Android Emulator, providing the following functionalities:
    - Starts the emulator
    - Shuts down the emulator
    - Reboots the emulator
    :param interactive: Controls interaction with the device (True for interaction, False for no interaction).
    :param avd_device_name: The name of the Android Emulator device.
    """

    def __init__(self, interactive: bool, avd_device_name: str) -> None:
        self.avd_device_name: str = avd_device_name
        self.interactive = interactive
        self.process: subprocess.Popen = None
        self.is_started = False

    def emulator_command(self, command: str, log: bool) -> subprocess.Popen:
        """
        This function executes emulator commands using subprocess.Popen and returns a subprocess object.
        This is valuable for accessing the process ID (PID), logs, and error information.

        :param command: is the command to execute
        :param log: is to enable logging
        :return: the subprocess.Popen with the command of the process and the pid
        """
        with open(_get_log_file_path(), 'w') as log_file:
            android_process = subprocess.Popen(  # noqa: S602
                [command],
                stdout=log_file if log else None,
                stderr=log_file if log else None,
                shell=True,
                preexec_fn=os.setpgrp,
            )

        self.process = android_process
        return self.process

    def start_emulator(self, snapshot: str = None, log: bool = True) -> subprocess.Popen:
        """
        This function starts the emulator in a subprocess. This process is returned.
        :param snapshot: Can be used to start the emulator from a given snapshot.
        :param log: If True, the output of the emulator subprocess will be logged to a file. True by default.
        :return: The subprocess in which the emulator is running
        """

        device_name = _check_device_name(self.avd_device_name)
        logger.info(f'Starting device {device_name}')

        command_parts = [EMULATOR, '-no-metrics', '-avd', self.avd_device_name]

        if not self.interactive:
            command_parts.append('-no-window')
        if snapshot:
            command_parts.append(f'-snapshot {snapshot}')

        emulator_command = ' '.join(command_parts)
        logger.info(f'Device is booting with command "{emulator_command}"')
        return self.emulator_command(emulator_command, log)

    def shutdown_emulator(self) -> bool:
        """
        This function allows you to power off the Android Emulator by utilizing the process ID (PID) of the subprocess.
        :return: It will return a boolean with True or False. It will also change the is_started, in order to know
        if the device is turned off or not.
        """
        try:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            logger.info(f'Device: {self.avd_device_name} was turned off...')
            self.is_started = False
            return True
        except subprocess.CalledProcessError:
            logger.error(f'Failed to shutdown the emulator: {self.avd_device_name}')
            return False

    def reboot_emulator(self, snapshot: str = None) -> subprocess.Popen:
        """
        This function reboots the emulator. By starting the shutdown_emulator and starting the emulator.
        :param snapshot: is optional if you want to reboot with a custom snapshot. This is None by default.
        """
        self.shutdown_emulator()

        logger.info('Wait a few seconds before restarting...')
        sleep(2)

        return self.start_emulator(snapshot=snapshot)
