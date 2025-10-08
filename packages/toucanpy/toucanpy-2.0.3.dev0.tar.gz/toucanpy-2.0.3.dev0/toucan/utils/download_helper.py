import atexit
import tempfile
from pathlib import Path

import requests as requests
from requests import Session

from toucan.utils import SSL_VERIFY, logger


def init_session() -> Session:
    """
    Initialize request session with the right headers.
    :return: the request session
    """
    session = requests.Session()
    session.headers.update(
        {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    )
    session.verify = SSL_VERIFY
    return session


def download_file(url: str) -> Path:
    """
    Downloads a file and will return the Path to the location of the downloaded file.
    The downloaded file is a TEMPORARY FILE, and will be deleted when the Python process terminates. If you wish to keep
    the file, you should copy it.
    :returns: a Path to the downloaded file.
    """
    # create session
    session = init_session()
    session.headers.update({'Accept-Encoding': 'gzip, deflate, br'})
    logger.info(f'Downloading apk file: {url}')
    apk = session.get(url, verify=False)
    if apk is None:
        raise LookupError('Apk file was not downloaded, please verify the url.')
    # create temp file that will be deleted at exit, return that file
    temp_file = tempfile.NamedTemporaryFile(delete=True)
    atexit.register(temp_file.close)
    temp_file.write(apk.content)
    return Path(temp_file.name)
