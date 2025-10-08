import logging
import os
import pathlib

from dotenv import load_dotenv


PACKAGE_ROOT = pathlib.Path(__file__).parent.parent.resolve()
PROJECT_ROOT = PACKAGE_ROOT.parent
RESULTS_ROOT = PROJECT_ROOT / 'results'
ANDROID_SDK_HOME = None


# define module level logger:
logger = logging.getLogger(__name__)


# INITIALISATION CODE
def _get_sdk_root():
    """
    Used to initialize ANDROID_SDK_ROOT, should not be called, use ANDROID_SDK_ROOT instead!
    This method looks for the location of your Android SDK. it does so by looking for commonly used environmental
    values and commonly used directories.
    If none of these guesses yield a result, an error is logged and the program terminates.
    :return: Our best guess as to the location of the Android SDK
    """
    # try finding a .env file to load any extra environment variables
    load_dotenv(override=True)

    # list of env values and paths that we look for the Android SDK. envs are checked before paths.
    environmental_values = ('ANDROID_SDK_ROOT', 'ANDROID_HOME')
    possible_paths = ('~/Android/Sdk',)

    for key in environmental_values:
        value = os.getenv(key)
        if value:
            logger.info(f'Using environmental value {key} for Android SDK ROOT {value}')
            return value

    for path in possible_paths:
        if '~' in path:
            path = os.path.expanduser(path)
        if os.path.isdir(path):
            logger.info(f'Using Android SDK ROOT {path}')
            return path

    # temporary fix: throw a warning instead of fatal. Problem is that tests fail when they need anything from utils, as
    # the init is then called.
    # TODO TOUCAN-70 move this function out of the utils __init__.
    logger.warning(
        f'Could not determine Android SDK ROOT. Define it in one of these env values: {environmental_values}, '
        f'or install the Sdk in one of these locations: {possible_paths}'
    )


def fatal(message):
    logger.error(message)
    logger.error('Exiting...')
    exit(1)


ANDROID_SDK_HOME = _get_sdk_root()

SSL_VERIFY = True
