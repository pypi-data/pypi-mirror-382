from abc import ABC, abstractmethod

from adb_pywrapper.adb_result import AdbResult


class BaseDevice(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        This method SHOULD NOT start the device. Use self.start() for this.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_files(self, files: list[str], destination_folder: str, version: str, app_name: str) -> list[str]:
        """
        Copy files from the device to a location on disk (e.g. Whatsapp database files).

        :param files: Path to the files that will be pulled
        :param destination_folder: The path where the database files should be copied to
        :param version: The app version at time of pulling
        :param app_name: The app name of which the files are pulled
        :return: The database files in a string list:
        """
        ...

    @abstractmethod
    def install(self, installation_file: str, r: bool = False) -> AdbResult:
        """
        Installs a given installation file on this device.

        :param installation_file: the location fo the file on the local machine
        :param r: -r option: replace already installed application. This is needed on physical devices or
                             if you get an error that the application already exists and should be uninstalled first.
        :return: the completed process of 'adb install [-r] {apk_path}'
        """
        ...
