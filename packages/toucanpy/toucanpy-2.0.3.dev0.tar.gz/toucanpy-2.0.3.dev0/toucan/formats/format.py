import sqlite3
import subprocess
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from os.path import basename
from pathlib import Path
from types import MappingProxyType

from adb_pywrapper.adb_device import AdbDevice

from toucan.formats import logger


class UiChangedError(Exception):
    """
    Exception that needs to be thrown when the UI of an app changes in such a way the programmed actions can no longer
    be executed. When this exception is thrown, Toucan can report that the UI was changed.
    """

    def __init__(self, message: str, screenshot: str = None):
        self.message = message
        self.screenshot = screenshot
        super().__init__(self.message)


@dataclass(frozen=True)
class ToucanFile:
    """
    A ToucanFile represents a file Toucan needs to keep track of for a given app.
    Every ToucanFile defines three aspects:
        * The path of that file on the device.
        * The expected file type: this is the file type we expect the recognition code to return, eg a file
          command-based implementation would return "SQLite 3.x database" for the Whatsapp contacts DB.
        * A set of parsing rules (at least one): these are the rules checks you want to perform on the parsing result.
          A parsing rule has a name (unique for this ToucanFile), and a Callable which will take a parsing result
          and return True or False, based on whether the contents are as expected.
    The fields of this class are immutable. You can create this class directly, or use the Builder (see the class
    ToucanFileBuilder).
    """

    file_path: Path
    expected_type: str
    parsing_rules: dict[str, Callable[[str], bool]]

    def verify_type(self, actual_type: str) -> bool:
        return self.expected_type == actual_type

    def verify_parsed_result(self, parsing_result: str) -> dict[str, bool]:
        return {name: rule(parsing_result) for name, rule in self.parsing_rules.items()}

    def pull(self, adb_device: AdbDevice, destination_folder: str) -> Path:
        pulled_file = adb_device.pull(str(self.file_path), destination_folder)
        # TODO TOUCAN-167: in case any pull fails, we should stop analysis of this ToucanFile
        # and continue with the next one.
        if not pulled_file.success:
            logger.fatal(f'Could not pull file: {self.file_path}')

        return Path(destination_folder) / basename(self.file_path)

    def __eq__(self, other):
        if not isinstance(other, ToucanFile):
            return False
        # Compare the dictionaries (or their immutable equivalents)
        return (
            self.file_path == other.file_path
            and self.expected_type == other.expected_type
            and self.parsing_rules == other.parsing_rules
        )

    def __hash__(self):
        return hash((self.file_path, self.expected_type))


class ToucanSqliteFile(ToucanFile):
    def pull(self, adb_device: AdbDevice, destination_folder: str) -> Path:
        # we also want to pull related files like .wal and .journal
        related_files_list = sorted(set(adb_device.ls(f'{self.file_path}*')))

        pulled_files = adb_device.pull_multi(related_files_list, destination_folder)

        successful_files = []
        for pulled_file in pulled_files:
            # TODO TOUCAN-167: in case any pull fails, we should stop analysis of this ToucanFile
            # and continue with the next one.
            if pulled_file.success:
                successful_files.append(pulled_file)

        if not successful_files:
            logger.fatal(f'Could not pull any file: {self.file_path}*')

        filename = basename(self.file_path)
        logger.info(
            f'Vacuuming pulled files. main file: {filename}, all files: {[basename(f.path) for f in pulled_files]}'
        )
        self._vacuum(filename, destination_folder)
        return Path(destination_folder) / filename

    @staticmethod
    def _vacuum(filename: str, destination_folder: str):
        absolute_path = f'{destination_folder}/{filename}'
        try:
            result = subprocess.run(['sqlite3', absolute_path, 'VACUUM;'])  # noqa: S603, S607
            result.check_returncode()
        except Exception as e:
            logger.exception(e)
            logger.warning('Vacuuming on command line failed, trying again through Python sqlite3')
            with sqlite3.connect(absolute_path, isolation_level=None) as conn:
                conn.execute('VACUUM;')


class ToucanFileBuilder:
    """
    A Builder class for ToucanFile.
    """

    def __init__(self):
        self.file_path: Path = None
        self.expected_type: str = None
        self.rules: dict[str, Callable[[str], bool]] = {}
        self.is_sqlite_file: bool = False

    def with_file_path(self, file_path: Path) -> 'ToucanFileBuilder':
        self.file_path = file_path
        return self

    def with_expected_type(self, expected_type) -> 'ToucanFileBuilder':
        self.expected_type = expected_type
        return self

    def add_rule(self, name: str, validation: Callable[[str], bool]) -> 'ToucanFileBuilder':
        if name in self.rules.keys():
            raise ValueError(f'Cannot add rule with name {name} as a rule with that name already exists.')
        self.rules[name] = validation
        return self

    def is_sqlite(self):
        self.is_sqlite_file = True
        return self

    def build(self) -> ToucanFile:
        if not self.file_path:
            raise ValueError('ToucanFile needs a file path')
        if not self.expected_type:
            raise ValueError('ToucanFile needs a an expected type')
        if not self.rules:
            raise ValueError('ToucanFile needs at least one parsing rule')
        if self.is_sqlite_file:
            return ToucanSqliteFile(
                file_path=self.file_path, expected_type=self.expected_type, parsing_rules=MappingProxyType(self.rules)
            )
        else:
            return ToucanFile(
                file_path=self.file_path, expected_type=self.expected_type, parsing_rules=MappingProxyType(self.rules)
            )


class ToucanFormat(ABC):
    """
    This class represents a format Toucan needs to keep track of.
    This class contains all format-specific knowledge Toucan needs:
        * The name and package name of the application
        * The files Toucan needs to keep track of (see ToucanFile)
        * Logic to fetch the latest version of the application
        * Logic to perform actions in the app after an update has been installed
        * Logic to perform file recognition
        * Logic to parse the files
        * Logic to judge whether recognition and parsing are still done properly
    Adding a new ToucanFormat will mean you need to make a new implementation of this abstract base class.
    """

    def __init__(self, app_name: str, package_name: str, toucan_files: list[ToucanFile]):
        self.app_name = app_name
        self.package_name = package_name
        self.toucan_files = toucan_files

    @abstractmethod
    def get_latest_version(self) -> str:
        """
        Returns the latest available version of the application this ToucanFormat covers.
        The returned string needs to be the version string from the apk that can be downloaded.
        :return: the latest available version of this application
        """
        pass

    @abstractmethod
    def get_latest_apk(self, store_path: Path):
        """
        Gets the latest available version of the application to a given location.
        After calling this method, and it was executed successfully, the apk should be stored in the given location.
        If anything goes wrong, this method should raise an exception.
        :param store_path: the full absolute path the file should be stored at. Includes the file name.
        """
        pass

    @abstractmethod
    def execute_actions(self, alice: str, bob: str):
        """
        Executes actions on the Toucan devices Alice and Bob, like sending messages back and forth, or making a call.
        This method should execute these actions given references to two emulators for alice and bob.
        The connection to the device needs to be made by this method (over ADB or Appium), after which all required
        actions should be executed.
        When the UI has changed in such a way these actions can no longer be executed, this method should raise a
        UiChangedException.
        Actions can be executed on Alice and Bob, or just Alice if no second device is needed. Keep in mind that Toucan
        will pull files ONLY from Alice.
        :param alice: the device ID of Alice
        :param bob: the device ID of Bob.
        """
        pass

    @abstractmethod
    def recognize_file(self, path_to_file: Path) -> str:
        """
        This method should apply file recognition, returning the file type. eg "Jpeg" or "sqlite3".
        :return: The file type of the given file
        """
        pass

    @abstractmethod
    def parse_file(self, path_to_file: Path) -> str:
        """
        This method should parse the given file, store the parsing results in one file, and return results.
        :return: The parsing result
        """
        pass
