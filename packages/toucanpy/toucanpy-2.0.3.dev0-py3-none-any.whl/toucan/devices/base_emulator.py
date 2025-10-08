import time
from abc import ABC, abstractmethod

from adb_pywrapper.adb_result import AdbResult

from toucan.devices import logger
from toucan.devices.base_device import BaseDevice
from toucan.utils.time_utils import get_current_time


class BaseEmulator(BaseDevice, ABC):
    REBOOT_WAIT_TIME_SECONDS = 2
    SNAPSHOT_PREFIX = 'toucan_run_'
    """
    An Abstract Base Class describing an emulator.

    Every emulator should inherit from this class and implement all methods decorated with `@abstractmethod`.
    Optionally, you can override the methods and properties that are not decorated.
    You can also implement your own methods.
    """

    def __enter__(self):
        """
        Called when an emulator is used in a with block, for example:

        ```py
        with DerivedEmulator(...) as emulator:
            ... # do things with emulator
        ```

        Together with the __exit__ method, this class becomes a context manager.
        """
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> bool:
        """
        Called when an emulator's with block is exited or when an exception is raised.

        The three parameters contain information about the exception.
        If the with-block is exited without exceptions, all three values are None.

        :param exception_type: The type of the exception, e.g. SyntaxError
        :param exception_value: The exception itself (converting this to a string will give you the error message)
        :param traceback: The traceback to the exception
        :return: True if no exceptions were found; if False, Python re-raises the exception automatically
        """
        if exception_type is not None:
            logger.error(str(exception_value))
            self.shutdown_emulator()
            return False

        return True

    @abstractmethod
    def start_emulator(self, custom_snapshot: str = None, log=True):
        """
        Start the emulator.

        Should start the emulator (if a snapshot is given, from the `custom_snapshot` image) and return its name.
        :param custom_snapshot: if given, start the emulator using the snapshot with this name
        :param log: is to log the process, this is by default on.
        :return: the name of the emulator; if not given, the emulator was not started correctly
        """
        ...

    @abstractmethod
    def shutdown_emulator(self):
        """
        This function allows you to power off the Emulator by utilizing the process ID (PID) of the subprocess.
        """
        ...

    def reboot_emulator(self, snapshot: str = None) -> bool:
        """
        Reboot the device.

        Note that this is *not* an abstract method: the called methods `start_emulator` and `shutdown_emulator` always
        have an implementation, because they are abstract methods.
        This method can be overridden if there's a more efficient way to reboot the device you're adding to Toucan.
        """
        self.shutdown_emulator()

        logger.info('Wait a few seconds before restarting...')
        time.sleep(self.REBOOT_WAIT_TIME_SECONDS)

        return self.start_emulator(custom_snapshot=snapshot)

    @abstractmethod
    def snapshots_list(self, filename_glob_pattern: str | None) -> list[str]:
        """
        Get the names of all available snapshots.

        :param filename_glob_pattern: The prescribed format for a snapshot name, e.g. "Toucan_run_*"
            Tip: when using `pathlib.Path` objects, you can pass this argument directly as a parameter.
        :return: a list of names of all available snapshots.
        """
        ...

    @abstractmethod
    def snapshot_delete(self, delete: list[str] = None) -> AdbResult:
        """
        Delete snapshots based on a list.
        If some but not all provided snapshots are removed success will be False, and a list of invalid snapshots
        is passed as a stderr.
        :param delete: a list containing snapshot names (str) to be deleted. Example: ['snap_name_1','snap_name_3']
        :return: AdbResult object with stdout, stderr if applicable and success True/False
        """
        ...

    @abstractmethod
    def snapshot_save(self, snapshot_name: str) -> AdbResult:
        """
        Create a snapshot of the current state of the emulator.
        :param snapshot_name: The name of the snapshot.
        :return: AdbResult object with stdout, stderr if applicable and success True/False.
        """
        ...

    @abstractmethod
    def snapshot_load(self, snapshot_name: str) -> AdbResult:
        """
        Load a snapshot of the emulator.
        :param snapshot_name: The name of the snapshot.
        :return: AdbResult object with stdout, stderr if applicable and success True/False.
        """
        ...

    @abstractmethod
    def snapshot_revert_to_latest_successful(self):
        """
        Reverts to the most recent successful run snapshot.
        """
        revert = self.snapshot_load('LATEST')
        if revert.success:
            logger.info('Reverted to the snapshot created after the last successful Toucan run')
        else:
            logger.error('Failed to revert to the latest snapshot (has Toucan already run successfully at least once?')
            logger.error(revert.stderr)

    @abstractmethod
    def snapshot_run_successful(self, debug_mode: bool = False):
        """
        Makes a new snapshot after a successful run.
        :param debug_mode: If True, do not overwrite the LATEST snapshot in debug mode.
        """
        if debug_mode:  # when in debug mode do not touch any the snapshots
            return

        new_snapshot_name = f'{self.SNAPSHOT_PREFIX}{get_current_time()}'
        snapshot_list = self.snapshots_list('toucan_run_')

        self.snapshot_delete(['LATEST'])
        self.snapshot_save('LATEST')

        while len(snapshot_list) > 2:
            oldest_snapshot = self._get_oldest_snapshot(self.SNAPSHOT_PREFIX)
            self.snapshot_delete([oldest_snapshot])
            logger.info(f'Removed outdated snapshot {oldest_snapshot} since it was over 2 runs old')
            snapshot_list.remove(oldest_snapshot)

        self.snapshot_save(new_snapshot_name)

    def _get_oldest_snapshot(self, prefix: str) -> str:
        """
        Get the oldest snapshot with a specific prefix.
        Snapshots should always be of the format <prefix>_<date> and are sorted by alphabet
        since the time format supports this.
        :param prefix: The prefix of the snapshots.
        :return: Name of the latest snapshot.
        """
        snapshots = self.snapshots_list(prefix)
        return min(snapshots)
