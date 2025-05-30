import json
import os
import requests
import requests_mock
import tempfile
import pytest
import shutil
from bs4 import BeautifulSoup


URL = 'https://ru.hexlet.io/courses'
ASSETS_DIR = 'ru-hexlet-io-courses_files'
CONTENT_FILE = 'ru-hexlet-io-courses.html'
HTTP_ERROR_CODES = 400, 401, 403, 404, 405, 408, 500, 501, 502, 503, 504, 505

current_file_directory = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_file_directory, 'asset.json')) as f:
    ASSETS = json.load(f)


def compare_prettified_htmls(html_content1, html_content2):
    soap1 = BeautifulSoup(html_content1, 'html.parser')
    soap2 = BeautifulSoup(html_content2, 'html.parser')
    return soap1.prettify() == soap2.prettify()


@pytest.fixture
def retrieved_content(filename):
    with open(os.path.join(current_file_directory, filename)) as f:
        return f.read()


@pytest.fixture
def expected_content():
    with open(os.path.join(current_file_directory, 'expected.html')) as f:
        return f.read()


@pytest.fixture
def cleanup_downloaded_files():
    yield

    if os.path.isfile(CONTENT_FILE):
        os.remove(CONTENT_FILE)
    if os.path.isdir(ASSETS_DIR):
        shutil.rmtree(ASSETS_DIR)


@pytest.fixture
def setup_mocking(retrieved_content):
    with requests_mock.Mocker() as m:
        m.get(URL, text=retrieved_content)
        m.get(ASSETS[-1]['url'], text=retrieved_content)  # href="/courses"
        for asset_data in ASSETS:
            if asset_data['url'].endswith('html'):
                asset_data['content'] = retrieved_content
            m.get(asset_data['url'], text=asset_data['content'])
        return m


@pytest.fixture
def temp_directory():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir


@pytest.fixture
def setup_mocking_http_fail_response(status_code):
    with requests_mock.Mocker() as m:
        m.get(URL, status_code=status_code)
        return m


@pytest.fixture
def setup_mocking_request_exception():
    with requests_mock.Mocker() as m:
        m.get(URL, exc=requests.exceptions.RequestException(
            'Some simulated RequestException'))
        return m
