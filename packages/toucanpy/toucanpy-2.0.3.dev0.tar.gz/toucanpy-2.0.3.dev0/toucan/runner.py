import logging
import os
from pathlib import Path
from time import sleep

from toucan.config import ToucanConfig
from toucan.devices.android.toucan_android_device import ToucanAndroidDevice
from toucan.devices.emulator_service import get_file_from_emulator, shut_down_emulator, start_emulators, update_app
from toucan.formats.format import ToucanFormat
from toucan.reporter.application_result import ApplicationResult, pretty_print
from toucan.reporter.reporter import Reporter
from toucan.utils import RESULTS_ROOT, versions
from toucan.utils.time_utils import get_current_time
from toucan.utils.versions import get_installed_app_version


logger = logging.getLogger(__name__)


class ToucanRunner:
    def __init__(self, formats: list[ToucanFormat], reporter: Reporter, config: ToucanConfig):
        """
        Initialize a ToucanRunner instance.
        After initialization, the run() method can loop through ToucanFormats and runs the Toucan workflow on them.

        :param formats: List of ToucanFormats to run
        :param reporter: the instance that reports the results
        :param config: config dict
        """
        # process every ToucanFormat
        self.formats: list[ToucanFormat] = formats
        self.reporter = reporter
        self.alice: ToucanAndroidDevice = None
        self.bob: ToucanAndroidDevice = None
        self.result_folder: Path = Path()
        self.current_version: str = ''
        self.latest_version: str = ''
        self.timestamp = get_current_time()
        self.config = config
        self.debug_snapshot_name = self.config.debug_snapshot_name
        self.toucan_snapshot_name = 'toucan_snapshot' if self.config.use_snapshots else None

    def run(self, interactive: bool = False, debug: bool = False):
        """
        Main method. We loop through the ToucanFormats and process them. The results are stored in the daily summary.
        :param interactive: if True, the emulator will open a window showing the phone display. Otherwise, the emulator
        will run headless.
        :param debug: if true, a dry run will be executed. This means that a snapshot of the emulator will be saved and
        put back at the end of the run, and the results will not be published.
        """
        logger.info('Starting run.')
        self.alice, self.bob = start_emulators(self.config, interactive, snapshot=self.toucan_snapshot_name)
        if debug:
            self.alice.snapshot_save(self.debug_snapshot_name)
            self.bob.snapshot_save(self.debug_snapshot_name)

        try:
            results = [self.run_toucan_format(toucan_format, debug) for toucan_format in self.formats]

            # Publish results
            if not debug:
                logger.info('Publishing all results to the Toucan daily')
                self.reporter.report_results(results)
            else:
                logger.info('Debug run of Toucan completed, not pushing application results to daily summary')
                logger.info(f'ApplicationResults: {pretty_print(results)}')
        finally:
            # shut down emulators
            for emulator in [self.alice, self.bob]:
                shut_down_emulator(emulator, debug, self.debug_snapshot_name, self.toucan_snapshot_name)

    def run_toucan_format(self, toucan_format: ToucanFormat, debug: bool = False) -> ApplicationResult:
        """
        Process a Toucan format. The following steps are done here:
        0. Make a snapshot of the current state of the emulators
        1. Check if there is a new version to install
        2. If so, install the version on the emulators
        3. Run the action script on the emulators
        4 Get the results:
            4a. Get the relevant files from the Alice emulator
            4b. Run recognition and parsing on the files
            4c. Validate the results from the previous step
        5. Store the results, so they can be sent to the daily report

        If anything went wrong, the snapshots that were taken in step 0 will be loaded on the emulators.
        Snapshots will not be saved if debug mode is on, or use_snapshots is set to False.

        :param toucan_format: the format to process
        :param debug: If in debug mode, no intermediate snapshots will be taken
        :return: the ApplicationResult for the processed format
        """
        logger.info(f'Starting analysis of ToucanFormat {toucan_format.app_name}')

        # Save snapshot
        if not debug and self.toucan_snapshot_name:
            logger.info(f'Making snapshot before updating {toucan_format.app_name}')
            self.alice.snapshot_save(self.toucan_snapshot_name)
            self.bob.snapshot_save(self.toucan_snapshot_name)

        file_results = {}
        try:
            if no_new_version_result := self._handle_no_new_version(toucan_format):
                return no_new_version_result

            self._install_latest_version(toucan_format)
            self._execute_actions(toucan_format)
            # TODO TOUCAN-167: report failures
            self._get_file_results(toucan_format, file_results)
            self._store_support(toucan_format, file_results)
            return ApplicationResult(toucan_format.app_name, self.latest_version, file_results)
        except Exception as e:
            logger.error(
                f'Something went wrong while running Toucan for application {toucan_format.app_name}: {e}',
                exc_info=True,
            )
            if not debug and self.toucan_snapshot_name:
                logger.info(f'Reverting to snapshot state before updating {toucan_format.app_name}')
                self.alice.snapshot_load(self.toucan_snapshot_name)
                self.bob.snapshot_load(self.toucan_snapshot_name)
            return ApplicationResult.error(toucan_format.app_name, self.latest_version)

    def _store_support(self, toucan_format: ToucanFormat, file_results: dict):
        """
        Store a file if the application is still supported.

        :param toucan_format: The application that was checked
        """
        if any(
            not recog_result or not all(parse_result.values()) for recog_result, parse_result in file_results.values()
        ):
            return

        # If all checks returned True, create empty file to signal that we still have support
        with open(self.result_folder / f'{toucan_format.app_name}_supported.txt', 'w'):
            pass

    def _execute_actions(self, toucan_format: ToucanFormat):
        # run actions on devices
        logger.info(f'Executing UI actions for app {toucan_format.app_name}')
        try:
            toucan_format.execute_actions(self.alice.adb_device.device, self.bob.adb_device.device)
        except Exception as e:
            # make screenshot whenever a problem occurs with the UI actions
            screenshot_name = f'ui_error_{toucan_format.app_name}_{self.timestamp}'
            self.alice.adb_device._command(
                f'exec-out screencap -p > {str(RESULTS_ROOT / "log" / f"{screenshot_name}_self.alice.png")}'
            )
            self.bob.adb_device._command(
                f'exec-out screencap -p > {str(RESULTS_ROOT / "log" / f"{screenshot_name}_bob.png")}'
            )
            raise e
        logger.info(
            f'UI actions for app {toucan_format.app_name} are executed. Waiting for a second before extracting files'
        )
        sleep(1)

    def _install_latest_version(self, toucan_format: ToucanFormat):
        self.result_folder = RESULTS_ROOT / toucan_format.app_name / self.latest_version / self.timestamp
        self.result_folder.mkdir(exist_ok=True, parents=True)

        apk_path = self.result_folder / f'{toucan_format.package_name}_v{self.latest_version}.apk'
        logger.info(f'Downloading latest apk of app {toucan_format.app_name}')
        toucan_format.get_latest_apk(apk_path)
        # TODO TOUCAN-167: check if update returns True
        update_app(apk_path, self.alice.adb_device)
        update_app(apk_path, self.bob.adb_device)

    def _handle_no_new_version(self, toucan_format):
        self.current_version = get_installed_app_version(toucan_format.package_name, self.alice.adb_device)
        self.latest_version = toucan_format.get_latest_version()
        if not versions.is_newer_version(self.latest_version, self.current_version):
            logger.info(f'Latest version {self.latest_version} not newer than installed version {self.current_version}')
            if not self.latest_version == self.current_version:
                logger.info(
                    f'Latest version {self.latest_version} is lower than the version of previous run, '
                    f'skipping {toucan_format.app_name}.'
                )
                return ApplicationResult.new_old_version(toucan_format.app_name, self.latest_version)

            if self._version_supported(toucan_format.app_name):
                logger.info(
                    f'Latest version {self.latest_version} was supported in previous run, '
                    f'skipping {toucan_format.app_name}.'
                )
                return ApplicationResult(toucan_format.app_name)
            else:
                logger.info(f'Latest version {self.latest_version} was not supported in previous run, running again.')
                return None
        return None

    def _version_supported(self, app_name: str) -> bool:
        """
        Check if the given app version was deemed as supported in a previous run.
        If it was, an empty file named 'appname_supported.txt' was stored in the result folder.
        If any previous run concluded we supported the given version, this method returns True.

        :param app_name: The name of the app for which the results are checked
        """
        version_result_folder = self.reporter.report_root / app_name / self.current_version
        if os.path.exists(version_result_folder):
            result_folders = sorted(
                [os.path.join(version_result_folder, file) for file in os.listdir(version_result_folder)], reverse=True
            )
            result_folders = [f for f in result_folders if os.path.isdir(f)]
            if result_folders[0]:
                if f'{app_name}_supported.txt' in os.listdir(result_folders[0]):
                    return True
        return False

    def _get_file_results(self, toucan_format: ToucanFormat, file_results):
        for toucan_file in toucan_format.toucan_files:
            logger.info(f'Pulling file {toucan_file.file_path}...')
            destination_file = get_file_from_emulator(
                self.alice, toucan_file, str(self.result_folder), toucan_format.app_name, self.latest_version
            )

            logger.info(f'Starting recognition for {toucan_file.file_path.name}')
            recognition_result = toucan_format.recognize_file(destination_file)
            logger.info(f'Starting parsing for {toucan_file.file_path.name}')
            parsing_result = toucan_format.parse_file(destination_file)

            logger.info('Storing recognition and parsing results')
            self._store_results(recognition_result, parsing_result, toucan_file.file_path.name)

            logger.info(f'Verifying recognition and parsing results for {toucan_file.file_path.name}')
            file_results[toucan_file] = (
                toucan_file.verify_type(recognition_result),
                toucan_file.verify_parsed_result(parsing_result),
            )

    def _store_results(self, recognition_result: str, parsing_result: str, file_name: str):
        """
        Store the recognition and parsing results for a ToucanFile in a given result folder.

        :param recognition_result: the recognition result
        :param parsing_result: the parsing result
        :param file_name: the name of the ToucanFile
        """
        # TODO TOUCAN-167: report failures
        with open(self.result_folder / f'{file_name}_recognition_result.txt', 'w') as parsing_file:
            parsing_file.write(recognition_result)
        with open(self.result_folder / f'{file_name}_parsing_result.txt', 'w') as parsing_file:
            parsing_file.write(parsing_result)
