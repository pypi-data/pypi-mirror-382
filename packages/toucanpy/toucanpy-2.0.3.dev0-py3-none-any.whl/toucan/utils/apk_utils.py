from functools import lru_cache
from pathlib import Path

from toucan.dependencies.aapt.aapt import get_apk_info
from toucan.utils import logger


@lru_cache
def get_apk_info_cached(apk_path: Path) -> dict[str, str]:
    """
    This is a cached wrapper for `aapt.get_apk_info`.
    """
    return get_apk_info(str(apk_path))


def get_apk_version(apk_path: Path) -> str:
    """
    Gets the app version from an apk file
    :param apk_path: path to apk file
    :return: the version
    """
    logger.info(f'Getting version for {apk_path}')
    return get_apk_info_cached(apk_path)['version_name']


def get_apk_package_name(apk_path: Path) -> str:
    """
    Gets the apk package name (e.g. com.example.app) from an apk file
    :param apk_path: path to apk file
    :return: the package name
    """
    logger.info(f'Getting package name for {apk_path}')
    return get_apk_info_cached(apk_path)['package_name']


def get_apk_app_name(apk_path: Path) -> str:
    """
    Gets the app name from an apk file (e.g. package com.whatsapp has the name WhatsApp)
    :param apk_path:  path to apk file
    :return: the app name
    """
    logger.info(f'Getting app name for {apk_path}')
    return get_apk_info_cached(apk_path)['app_name']
