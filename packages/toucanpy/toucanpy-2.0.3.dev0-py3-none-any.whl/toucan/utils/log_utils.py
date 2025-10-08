import logging
import sys
from datetime import datetime
from pathlib import Path

from toucan.utils import RESULTS_ROOT


_LOGGING_ALREADY_CONFIGURED = False


def load_default_log_config(
    log_level: int = logging.INFO, log_dir: Path = RESULTS_ROOT / 'log', ignore_already_set: bool = False
):
    global _LOGGING_ALREADY_CONFIGURED
    if _LOGGING_ALREADY_CONFIGURED and not ignore_already_set:
        raise Exception('Logging configuration cannot be called twice.')
    # Here we create the root logger. The configuration will be inherited by all loggers defined at module level:
    log_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    logging.basicConfig(
        handlers=[
            logging.FileHandler(log_dir / f'toucan_{now}.log'),
            logging.StreamHandler(sys.stdout),  # adding this handler makes sure the output is also printed to stdout
        ],
        level=log_level,
        format='%(asctime)s [%(levelname)s] <%(module)s.%(funcName)s>:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    if _LOGGING_ALREADY_CONFIGURED and ignore_already_set:
        logging.getLogger(__name__).warning(
            'Logging config was loaded while another config was loaded before. '
            'Please review the code to make sure you meant to do this.'
        )
    _LOGGING_ALREADY_CONFIGURED = True
