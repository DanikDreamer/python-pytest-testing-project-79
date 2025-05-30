from bs4 import BeautifulSoup
import json
import os
import requests

from . import url_utils
from .assets_processor import AssetsProcessor
from .logger import Logger
from .exceptions.network_exceptions import HttpError, RequestError
from .exceptions.io_exceptions import SaveError, DirectoryError

SETTINGS_FILE = 'settings.json'


class DownloadManager:
    def __init__(self, url, path):
        self.url = url
        self.path = path or ''
        self.__validate_path()

        self.page_content_filename = url_utils.filename_from_url(self.url)
        self.path_to_save_page_content = os.path.join(
            path, self.page_content_filename)
        self.assets_dir = url_utils.dirname_for_web_assets(
            url_utils.filename_from_url(self.url))
        self.logger = Logger(self.page_content_filename)

        self.soup = self.__get_soup()

        self.__log_attributes()

        if self.soup:
            self.__assets_processor = AssetsProcessor(self)
            self.__get_settings()

    def download(self):
        if not self.soup:
            return

        self.__assets_processor.download_assets()
        self.__download_page()
        return self.path_to_save_page_content

    def __download_page(self):
        processed_page_content = self.__process_page_content()
        self.__save_page_content(processed_page_content)

    def __process_page_content(self):
        return self.soup.prettify() if self.__prettify else str(self.soup)

    def __save_page_content(self, content):
        try:
            with open(self.path_to_save_page_content, 'w') as f:
                f.write(content)
            self.logger.debug(
                f"Page content from '{self.url}' downloaded successfully "
                f"and saved to '{self.path_to_save_page_content}'")

        except OSError as e:
            error_message = (f"Failed to save page content to "
                             f"{self.path_to_save_page_content}. Error: {e}")

            self.__assets_processor.remove_assets_dir()
            self.logger.debug(error_message)
            raise SaveError(error_message)

    def __get_soup(self):
        self.logger.debug(f"Start download from '{self.url}'")
        try:
            response = requests.get(self.url)
            if response.ok:
                return BeautifulSoup(response.text, 'html.parser')

            error_msg = (f'Failed to retrieve content. '
                         f'Server returned status code {response.status_code}')
            self.logger.debug(error_msg)
            raise HttpError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f'Failed to retrieve content. Error: {e}'
            self.logger.debug(error_msg)
            raise RequestError(error_msg)

    def __get_settings(self):
        settings_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), SETTINGS_FILE)
        with open(settings_path, 'r') as settings_file:
            self.__settings = json.load(settings_file)

        self.asset_tags = self.__settings['asset_tags']
        self.ignore_other_hosts = self.__settings['ignore_other_hosts']
        self.__prettify = self.__settings['prettify']

    def __validate_path(self):
        if self.path and not os.path.exists(self.path):
            raise DirectoryError(f"Directory '{self.path}' does not exist.")

    def __log_attributes(self):
        self.logger.debug(f'{self.__class__.__name__} initialized')
        self.logger.debug(f'Log level: {self.logger.log_level}')
        self.logger.debug(f'Log path: {self.logger.log_path}')
        self.logger.debug(f'page_content_filename:'
                          f'{self.page_content_filename}')
        self.logger.debug(f'path_to_save_page_content:'
                          f'{self.path_to_save_page_content}')
        self.logger.debug(f'assets_dir: {self.assets_dir}')
