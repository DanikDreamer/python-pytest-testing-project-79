import os

import pytest
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError

from page_loader import download


def read(file_path, binary=False):
    mode = "rb" if binary else "r"
    with open(file_path, mode) as f:
        return f.read()


def get_test_data_path(name):
    return os.path.join("tests/test_data", name)


def normalize_html(html_str):
    return BeautifulSoup(html_str, "html.parser").prettify()


def test_connection_error(requests_mock, tmp_path):
    url = "https://badsite.com"
    requests_mock.get(url, exc=ConnectionError)
    with pytest.raises(ConnectionError):
        download(url, tmp_path)


@pytest.mark.parametrize("status_code", [404, 500])
def test_response_with_error(status_code, requests_mock, tmp_path):
    url = f"https://site.com/{status_code}"
    requests_mock.get(url, status_code=status_code)
    with pytest.raises(HTTPError):
        download(url, tmp_path)


def test_storage_errors(requests_mock, tmp_path):
    url = "https://site.com/blog/about"
    requests_mock.get(url)

    with pytest.raises(PermissionError):
        download(url, "/sys")

    with pytest.raises(NotADirectoryError):
        download(url, f"{tmp_path}/site-com-blog-about.html")

    with pytest.raises(NotADirectoryError):
        download(url, f"{tmp_path}/notExistsPath")


def test_page_load(requests_mock, tmp_path):
    url = "https://ru.hexlet.io/courses"
    asset_url = "https://ru.hexlet.io/assets/professions/python.png"
    assets_dir = tmp_path / "ru-hexlet-io-courses_files"
    asset_filename = "ru-hexlet-io-assets-professions-python.png"
    asset_path = assets_dir / asset_filename

    html_before = read(get_test_data_path("before.html"))
    requests_mock.get(url, text=html_before)

    asset_data = read(get_test_data_path("logo.png"), binary=True)
    requests_mock.get(asset_url, content=asset_data)

    downloaded_html_page = download(url, tmp_path)

    expected_html = read(get_test_data_path("after.html"))
    actual_html = read(downloaded_html_page)

    assert os.path.exists(downloaded_html_page)
    assert normalize_html(actual_html) == normalize_html(expected_html)
    assert os.path.exists(asset_path)
    assert read(asset_path, binary=True) == asset_data
