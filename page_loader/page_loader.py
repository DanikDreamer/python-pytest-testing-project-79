import logging
import os
import re
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
ASSET_TAGS = {"img": "src",
              "link": "href",
              "script": "src",
              "video": "src",
              "audio": "src",
              "source": "srcset"}

class AssetNotFound(Exception):
    def __init__(self, message="AssetNotFound: Asset could not be downloaded"):
        super().__init__(message)

class RequestInvalidStatus(Exception):
    def __init__(self, message):
        super().__init__(message)


def modify_name(url, extension=True):
    logger.info(f'Creating name local name for: {url}')

    root, file_extension = os.path.splitext(url)
    file_extension = '.html' if file_extension == '' else file_extension
    # remove schema
    file_name = re.sub(r'^[a-zA-Z]+://', '', root)
    # change symbols to -
    file_name = re.sub(r'[^A-Za-z0-9]', '-', file_name)
    file_name = re.sub(r'[^A-Za-z0-9]+$', '', file_name)

    logger.info(f'Local name created: {file_name}')
    if extension:
        return file_name + file_extension
    return file_name


def download_asset(url, path_to_save):
    logger.info(f'Downloading asset... {path_to_save}')
    try:
        response = requests.get(url)
        logger.info(f'Server response: {response}')
        if response.ok:
            with open(path_to_save, 'wb') as f:
                f.write(response.content)
    except Exception as e:
        logger.info(f'Asset cannot be downloaded due to {e}')


def download_assets(soup, assets_dir_name, assets_dir_path, host, scheme):
    logger.info('Downloading assets...')
    for tag_type, attribute in ASSET_TAGS.items():
        asset_tags = soup.find_all(tag_type)
        for tag in asset_tags:
            # If tag has href or src attribute
            if tag.has_attr(attribute):
                parsed_url = urlparse(tag[attribute])
                if parsed_url.netloc == host or parsed_url.netloc == '':
                    asset_url = (
                        tag)[attribute] if scheme in tag[attribute] else (
                            scheme + '://' + host + tag[attribute])
                    asset_name = modify_name(url=asset_url)
                    full_asset_path = os.path.join(assets_dir_path, asset_name)
                    download_asset(url=asset_url, path_to_save=full_asset_path)
                    tag[attribute] = os.path.join(assets_dir_name, asset_name)
                    logger.info(
                        f'Asset downloaded correctly in: {full_asset_path}. '
                        f'Exists: {os.path.exists(full_asset_path)}')


def download_page(url):
    try:
        response = requests.get(url)
        logger.info(f'Server response: {response}')
        if response.ok:
            return response
    except Exception as e:
        logger.error(f'Target page cannot be downloaded due to {e}')
        raise Exception from e

def check_target_page_schema(url):
    parsed_url = urlparse(url)
    print(parsed_url)

def download(url: str, output: str = None):

    logger.info(f'Downloading the page {url}')
    check_target_page_schema(url)
    page = download_page(url)
    page_name = modify_name(url)
    output_folder = output if output else (
        os.path.join(os.path.dirname(__file__)))
    logger.info(f'Output folder: {output_folder}')
    target_page_path = os.path.join(output_folder, page_name)
    assets_dir_name = modify_name(url=url, extension=False) + '_files'
    assets_dir_path = os.path.join(output_folder, assets_dir_name)
    logger.info(f'Assets folder: {assets_dir_name}')
    soup = BeautifulSoup(page.text, "html.parser")
    if not os.path.exists(assets_dir_path):
        os.mkdir(assets_dir_path)
    parsed_url = urlparse(url)

    download_assets(soup=soup,
                    assets_dir_name=assets_dir_name,
                    assets_dir_path=assets_dir_path,
                    host=parsed_url.netloc,
                    scheme=parsed_url.scheme)

    final_page = str(soup.prettify())
    try:
        with open(target_page_path, "w", encoding="utf-8") as file:
            file.write(final_page)
    except PermissionError as e:
        raise Exception() from e
    logger.info(f'Target file exists: {os.path.exists(target_page_path)}')
    return target_page_path
