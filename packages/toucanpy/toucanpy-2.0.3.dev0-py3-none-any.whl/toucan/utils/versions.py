from adb_pywrapper.adb_device import AdbDevice
from packaging import version as packaging_version

from toucan.utils import logger


def is_newer_version(comp_version, ref_version):
    """
    Compares a version with a reference (former) version.
    :param comp_version: Version to compare.
    :param ref_version: Version to be compared to.
    :return: True if comp_version is larger than the reference version
    """
    if ref_version is None:
        return True
    return packaging_version.parse(comp_version) > packaging_version.parse(ref_version)


def get_installed_app_version(package_name: str, emulator: AdbDevice) -> str | None:
    """
    Gets the version number of an installed app given the package name
    :param package_name: the package name of the installed app to check
    :param emulator: the emulator to get the installed app from
    :return: the version currently installed
    """
    # TODO TOUCAN-167: report error when app isn't yet installed
    logger.info(f'Getting version for installed package {package_name} over adb')
    adb_output = emulator.shell(f'dumpsys package {package_name}')
    if adb_output.success:
        for line in adb_output.stdout.splitlines():
            if 'versionName' in line:
                installed_version = line.split('=')[-1]
                logger.info(f'Version found: "{installed_version}" (from line "{line}"')
                return installed_version
    # TODO TOUCAN-83: Fix case when stderr is Can't find service: package
    logger.error(
        f'Could not determine version for package {package_name}, adb output:\n'
        f'out: {adb_output.stdout}\n'
        f'err: {adb_output.stderr}\n'
        f'success: {adb_output.success}'
    )
