import os

import pytest
from requests.exceptions import ConnectionError, HTTPError

from page_loader import download


def read(file_path):
    with open(file_path, "r") as f:
        result = f.read()
    return result


def get_test_data_path(name):
    return os.path.join("tests/test_data", name)


@pytest.fixture(scope="module")
def expected_content():
    return read(get_test_data_path("index.html"))


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


def test_page_load(requests_mock, tmp_path, expected_content):
    url = "https://site.com/blog/about"
    requests_mock.get(url, text=expected_content)
    file_path = download(url, tmp_path)

    expected_file_path = os.path.join(tmp_path, "site-com-blog-about.html")
    actual_content = read(file_path)

    assert file_path == expected_file_path
    assert os.path.exists(file_path)
    assert actual_content == expected_content
