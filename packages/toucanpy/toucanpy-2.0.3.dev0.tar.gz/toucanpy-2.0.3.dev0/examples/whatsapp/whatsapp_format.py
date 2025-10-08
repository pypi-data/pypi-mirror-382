import shutil
import sqlite3
import subprocess
from pathlib import Path
from threading import Lock

import requests
from bs4 import BeautifulSoup
from puma.apps.android.whatsapp.whatsapp import WhatsappActions

from examples import logger
from toucan.formats.format import ToucanFileBuilder, ToucanFormat
from toucan.utils.download_helper import download_file
from toucan.utils.apk_utils import get_apk_version

APP_NAME = "WhatsApp"
PACKAGE_NAME = "com.whatsapp"
URL = "https://www.whatsapp.com/android"
DOWNLOAD_URL_DOMAIN = "https://scontent.whatsapp.net/"


class WhatsAppFormat(ToucanFormat):
    _downloaded_file: Path = None
    _download_lock = Lock()

    def __init__(self):
        """
        In the __init__, the ToucanFiles related to the format should be initialized. This can be done using the
        ToucanFileBuilder, which can help creating a ToucanFile.
        For WhatsApp, two database files will be available on the emulator, which we want to check.
        """
        super().__init__(APP_NAME, PACKAGE_NAME, toucan_files=[
            ToucanFileBuilder()
                         .with_file_path(Path('/data/data/com.whatsapp/databases/msgstore.db'))
                         .with_expected_type('SQLite 3.x database')
                         .is_sqlite()
                         .add_rule('expected_tables', lambda parsing_result: self._database_contains_tables(parsing_result, "message_system_group_auto_restrict, message_orphan"))
                         .build(),
            ToucanFileBuilder()
                         .with_file_path(Path('/data/data/com.whatsapp/databases/wa.db'))
                         .with_expected_type('SQLite 3.x database')
                         .is_sqlite()
                         .add_rule('expected_tables', lambda parsing_result: self._database_contains_tables(parsing_result, "wa_biz_profiles_call_hours, wa_profile_links_deny_list"))
                         .build()
        ])

    def execute_actions(self, alice: str, bob: str):
        """
        This method should be implemented for every ToucanFormat, to define which actions should be executed in an app
        on the emulator. The results of these actions should be available in the files that are retrieved from the
        emulator.

        This code below only opens the WhatsApp application on the emulator.

        If more actions need to be executed, you can either use Puma, which can help you execute actions for certain apps,
        or you can write custom code to execute actions.
        """
        logger.info('Opening WhatsApp')
        WhatsappActions(alice)

    def recognize_file(self, path_to_file: Path) -> str:
        """
        This method has to be implemented in any subclass of ToucanFile. This method can be used to see if a file is
        properly recognized.

        In this example, we use the `file` command and store the result, so this can be compared to the expected file
        type of the ToucanFile.
        """
        result = subprocess.run(['file', '-b', path_to_file], capture_output=True, text=True).stdout
        comma_index = result.index(',')
        return result[0:comma_index]

    def parse_file(self, path_to_file: Path) -> str:
        """
        This method can be used to check the contents of a file, and see if they are as expected.

        In this example, we check the database to see which tables it contains and store the results. This will be used
        later to validate the rules that were defined in the ToucanFile.
        """
        with sqlite3.connect(path_to_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            return ", ".join(table_names)

    def _get_apk(self) -> Path:
        """
        Either downloads the APK of the latest version of WhatsApp, or gets the previously downloaded APK.
        The downloaded file is a temporary file, and will be deleted when the program terminates.

        This method can be copied if you need to get APKs from the internet.
        """
        if not self._downloaded_file:
            with self._download_lock:
                if not self._downloaded_file:
                    apk_download_url = self._scrape_apk_download_url()
                    self._downloaded_file = download_file(apk_download_url)
        return self._downloaded_file

    def get_latest_version(self) -> str:
        """
        Determine version from the downloaded APK as it is not available on the website.

        This method can be copied if you need to get APKs from the internet.
        """
        return get_apk_version(self._get_apk())

    def get_latest_apk(self, store_path: Path):
        """
        Search for the latest APK file on the WhatsApp website.
        Then download this version to the APK cache folder.

        This method can be copied if you need to get APKs from the internet.

        :param store_path: the path to the directory where the APK needs to be stored
        :return: the local path to the downloaded APK
        """
        shutil.copy(self._get_apk(), store_path)

    @staticmethod
    def _scrape_apk_download_url() -> str:
        """
        Retrieves the download URL on the WhatsApp download page.
        Raises exception if the request to the URL fails or if a download link could not be found.

        This method can be copied if you need to get APKs from the internet.
        """
        response = requests.get(URL, verify=False)
        if not response.ok:
            raise Exception(f"Failed to load page {URL}, status code {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')

        download_link = None
        # Search for all <a> tags with href attributes
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Check if the href starts with the desired base URL
            if href.startswith(DOWNLOAD_URL_DOMAIN):
                download_link = href
                break

        if not download_link:
            raise Exception("Could not find the download link on the page.")
        return download_link

    @staticmethod
    def _database_contains_tables(parsing_result, expected_tables: str):
        """
        This method is specific for this example, and defines a rule that should be tested for this format. To test support
        and create other rules, more methods like this one can be created.
        """
        return expected_tables in parsing_result
