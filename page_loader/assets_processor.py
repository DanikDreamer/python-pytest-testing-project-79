import os
import shutil
import requests
from . import url_utils


class AssetsProcessor:
    def __init__(self, download_manager):
        self.__download_manager = download_manager
        self.__full_domain = url_utils.full_domain(self.__download_manager.url)
        self.__base_url = url_utils.base_url(self.__download_manager.url)
        self.__domain = url_utils.domain(self.__download_manager.url)
        self.__assets_dir = self.__download_manager.assets_dir

        self.__assets_path = url_utils.dirname_for_web_assets(
            self.__download_manager.path_to_save_page_content)

        self.__logger = self.__download_manager.logger
        self.__log_attributes()

    def download_assets(self):
        assets = self.__get_page_assets()

        if not assets or not self.__make_assets_dir():
            return

        processed_assets_results = [
            self.__process_asset(asset)
            for asset in assets
        ]
        processed_assets_exist = any(processed_assets_results)

        if not processed_assets_exist:
            self.__remove_assets_dir()

    def remove_assets_dir(self):
        try:
            shutil.rmtree(self.__assets_path)
            self.__logger.debug(
                f'Removed assets directory: {self.__assets_path}')
        except Exception as e:
            self.__logger.debug(
                f'Failed to remove assets directory: {self.__assets_path}: {e}')

    def __get_page_assets(self):
        return [asset for tag in self.__download_manager.asset_tags
                for asset in self.__download_manager.soup.find_all(tag)]

    def __process_asset(self, asset):
        asset_url = self.__get_asset_url(asset)

        if self.__should_ignore_host(asset_url):
            return False

        asset_full_url = self.__get_full_url(asset_url)
        path_to_save = self.__get_path_to_save_asset(asset_full_url)
        self.__download_asset(asset_full_url, path_to_save)
        self.__update_asset_link(asset, asset_full_url)
        return True

    def __should_ignore_host(self, asset_path):
        return self.__download_manager.ignore_other_hosts and \
            self.__is_other_domain(asset_path)

    def __update_asset_link(self, asset, asset_full_url):
        new_asset_link = self.__get_asset_updated_link(asset_full_url)
        asset_link_attr = self.__get_asset_link_attr(asset)
        asset[asset_link_attr] = new_asset_link

    def __get_asset_url(self, asset):
        asset_link_attr = self.__get_asset_link_attr(asset)
        url = asset.get(asset_link_attr)
        self.__logger.debug(f'Asset URL: {url}')
        return url

    # TODO: maybe refactor using page_loader.url_utils.full_url?
    def __get_full_url(self, asset_path):
        if not url_utils.extension(asset_path):
            asset_path = f"{asset_path.rstrip('/')}.html"

        if url_utils.domain(asset_path):
            self.__logger.debug(f'Asset is an absolute URL: {asset_path}')
            return asset_path

        if url_utils.is_absolute_path(asset_path):
            full_url = f'{self.__full_domain}{asset_path}'
            self.__logger.debug(f'Full URL for absolute path: {full_url}')
            return full_url

        full_url = f'{self.__base_url}{asset_path}'
        self.__logger.debug(f'Full URL for relative path: {full_url}')
        return full_url

    # TODO: test it
    def __make_assets_dir(self):
        try:
            os.makedirs(self.__assets_path)
            self.__logger.debug(
                f'Created assets directory: {self.__assets_path}')
            return True

        except OSError as e:
            self.__logger.debug(f'Failed to create assets directory: '
                                f'{self.__assets_path}. Error: {e}')
            return False

    # TODO: Maybe refactoring is needed again
    # TODO: Move an asset processing logic to a separate class
    def __get_asset_updated_link(self, asset_full_url):
        base_path_to_save = url_utils.filename_from_full_url(asset_full_url)
        updated_link = os.path.join(
            self.__download_manager.assets_dir, base_path_to_save)
        self.__logger.debug(f'Updated asset link: {updated_link}')
        return updated_link

    def __get_path_to_save_asset(self, asset_full_url):
        asset_new_link = self.__get_asset_updated_link(asset_full_url)
        path_to_save = os.path.join(
            self.__download_manager.path, asset_new_link)
        self.__logger.debug(f'Path to save asset: {path_to_save}')
        return path_to_save

    def __get_asset_link_attr(self, asset):
        asset_name = asset.name
        return self.__download_manager.asset_tags[asset_name]

    def __is_other_domain(self, asset_url):
        asset_domain = url_utils.domain(asset_url)
        return asset_domain != '' and asset_domain != self.__domain

    # TODO: test it
    def __download_asset(self, url, save_path):
        try:
            response = requests.get(url)
            if response.ok:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                self.__logger.debug(
                    f"asset file '{url}' downloaded successfully "
                    f"and saved to '{save_path}'")
            else:
                self.__logger.debug(
                    f"Failed to download asset file '{url}'"
                    f'Status code: {response.status_code}')
        except requests.exceptions.RequestException as e:
            self.__logger.debug(f"Failed to download asset file '{url}'. "
                                f"Error: {e}")

    def __log_attributes(self):
        self.__logger.debug(f'{self.__class__.__name__} initialized')
        self.__logger.debug(f'domain: {self.__domain}')
        self.__logger.debug(f'base_url: {self.__base_url}')
        self.__logger.debug(f'full_domain: {self.__full_domain}')
        self.__logger.debug(f'assets_path: {self.__assets_path}')
