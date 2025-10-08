import os
from os.path import basename
from pathlib import Path

from adb_pywrapper.adb_device import AdbDevice

from toucan.config import ToucanConfig
from toucan.devices import logger
from toucan.devices.android.toucan_android_device import ToucanAndroidDevice
from toucan.formats.format import ToucanFile
from toucan.utils.apk_utils import get_apk_app_name, get_apk_package_name, get_apk_version
from toucan.utils.versions import get_installed_app_version


class EmulatorService:
    def __init__(self, config: ToucanConfig, interactive: bool = False):
        self.interactive = interactive
        self.config = config

    def get_emulator_alice(self):
        return self.initialize_emulator(self.config.alice)

    def get_emulator_bob(self):
        return self.initialize_emulator(self.config.bob)

    def initialize_emulator(self, emulator_name):
        return ToucanAndroidDevice(emulator_name, self.config.wait_time, interactive=self.interactive)


def start_emulators(
    config: ToucanConfig, interactive: bool = False, snapshot: str = None
) -> tuple[ToucanAndroidDevice, ToucanAndroidDevice]:
    """
    Starts the Alice and Bob emulators, and returns them.

    :param config: toucan config containing the emulator names
    :param interactive: If emulator should be run in interactive mode
    :param snapshot: Name of the snapshot to start from
    """
    # start emulators
    emulator_service = EmulatorService(config, interactive)

    emulator_alice = None
    emulator_bob = None
    try:
        emulator_alice = emulator_service.get_emulator_alice()
        emulator_alice.start_emulator(snapshot)
        logger.info('Alice booted.')
        emulator_bob = emulator_service.get_emulator_bob()
        emulator_bob.start_emulator(snapshot)
        logger.info('Bob booted.')
    except Exception as e:
        if emulator_alice is not None:
            emulator_alice.shutdown_emulator()
        if emulator_bob is not None:
            emulator_bob.shutdown_emulator()
        raise e

    # TODO TOUCAN-167: report failures
    return emulator_alice, emulator_bob


def shut_down_emulator(emulator: ToucanAndroidDevice, debug: bool, debug_snapshot_name: str, toucan_snapshot_name: str):
    if debug:
        # restore debug snapshot
        emulator.snapshot_load(debug_snapshot_name)
        emulator.snapshot_delete([debug_snapshot_name])
    elif toucan_snapshot_name:
        emulator.snapshot_save(toucan_snapshot_name)
    emulator.shutdown_emulator()


def update_app(apk_path: Path, emulator: AdbDevice) -> bool:
    """
    Updates an app given an updated apk.

    :param apk_path: path to the apk to install
    :param emulator: the emulator to update
    :return: True if the update succeeded, False if it failed
    """
    app_name = get_apk_app_name(apk_path)
    package_name = get_apk_package_name(apk_path)
    old_version = get_installed_app_version(package_name, emulator)
    new_version = get_apk_version(apk_path)

    logger.info(f'About to update {app_name} ({package_name}) from version {old_version} to {new_version}')
    install_result = emulator.install(str(apk_path))
    logger.info(f'Updated {app_name}, adb output: {install_result.stdout}')
    return get_installed_app_version(package_name, emulator) == new_version


def get_file_from_emulator(
    emulator: ToucanAndroidDevice, toucan_file: ToucanFile, destination_folder: str, app_name: str, version: str
) -> Path:
    """
    Pull the files that should be processed from the given emulator. For SQLite databases, the files are vacuumed,
    so all data is in the main database file.

    :param emulator: the emulator the files should be pulled from (usually Alice)
    :param toucan_file: the ToucanFile for which the related files should be pulled
    :param destination_folder: the folder the pulled file should be stored in
    :param app_name: the name of the app in the ToucanFormat the files belong to
    :param version: the version of the APK (used for the final filename)
    :return: the Path of the stored file that is pulled from the emulator
    """
    adb_device = emulator.adb_device

    result_file = toucan_file.pull(adb_device, destination_folder)

    filename = basename(result_file)

    new_name = f'Toucan_{app_name}_v{version}_{filename}'
    destination_file = f'{destination_folder}/{new_name}'
    os.rename(f'{destination_folder}/{filename}', destination_file)

    return Path(destination_file)
