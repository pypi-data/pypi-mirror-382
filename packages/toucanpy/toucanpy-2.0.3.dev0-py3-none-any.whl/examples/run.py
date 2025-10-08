import argparse

from examples import logger
from examples.config import TOUCAN_CONFIG
from examples.whatsapp.whatsapp_format import WhatsAppFormat
from toucan.reporter.markdown_reporter import MarkdownReporter
from toucan.config import ToucanConfig
from toucan.runner import ToucanRunner
from toucan.utils import PROJECT_ROOT
from toucan.utils.log_utils import load_default_log_config

FORMATS = [
    WhatsAppFormat()
    # If you want to test multiple formats at once, they can be added to this list.
]

if __name__ == '__main__':
    """
    The main method is the entry point for Toucan. In this method, any arguments that were passed to Toucan should be
    parsed. A Reporter should be instantiated, so it can be used to report the results of a Toucan run. A ToucanRunner
    should also be instantiated, which will handle the actual run of Toucan.

    This example is a working example, and as such, you can run it to see how Toucan works.

    Toucan will only install an APK if it's newer than the APK currently installed on the emulator, or if verifying
    the results of the previous run showed that there was something wrong. The ToucanRunner will only run the verification
    steps if a new APK is installed. If you want to make sure that an APK is updated, you can remove the README.md in
    results/daily_summary/WhatsApp and results/daily_summary.
    """
    # load default log configuration
    load_default_log_config()
    # setup argument parser
    parser = argparse.ArgumentParser(description="Toucan")
    parser.add_argument('--interactive', action='store_true',
                        help="Run in interactive mode. This will open windows for the emulators so you can see the actions Toucan executes.",
                        default=False)
    parser.add_argument('--debug', action='store_true',
                        help="Run in debug mode. This will prevent results from being published to the daily report, and revert the emulators to the exact state before this run. Results are printed to stdout.",
                        default=False)
    args = parser.parse_args()
    try:
        reporter = MarkdownReporter(report_root=PROJECT_ROOT / 'results' / 'daily_summary',
                                    git_pull_and_push=False,
                                    destination_branch=TOUCAN_CONFIG['daily_report']['branch'])
        config = ToucanConfig(
            alice=TOUCAN_CONFIG['emulators']['alice'],
            bob=TOUCAN_CONFIG['emulators']['bob'],
            use_snapshots=TOUCAN_CONFIG['emulators']['use_snapshots'],
            debug_snapshot_name=TOUCAN_CONFIG['emulators']['debug_snapshot_name'],
            wait_time=TOUCAN_CONFIG['emulators']['wait_time']
        )
        toucan_runner = ToucanRunner(FORMATS, reporter, config)
        toucan_runner.run(interactive=args.interactive, debug=args.debug)
    except Exception as e:
        logger.exception(e)