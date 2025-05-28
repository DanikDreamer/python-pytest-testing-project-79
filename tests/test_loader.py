import os

import pytest
import requests_mock
from requests.exceptions import HTTPError, MissingSchema

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


def test_success_download(tmp_path, expected_content):
    url = "https://example.com/page"
    with requests_mock.Mocker() as m:
        m.get(url, text=expected_content)
        file_path = download(url, tmp_path)

    expected_file_path = os.path.join(tmp_path, "example-com-page.html")
    actual = read(expected_file_path)

    assert file_path == expected_file_path
    assert os.path.exists(file_path)
    assert actual == expected_content


def test_invalid_url(tmp_path):
    with pytest.raises(MissingSchema):
        download("not-a-url", tmp_path)


def test_http_error(tmp_path):
    url = "https://example.com/not-found"
    with requests_mock.Mocker() as m:
        m.get(url, status_code=404)

        with pytest.raises(HTTPError):
            download(url, tmp_path)


def test_write_permission_error(expected_content):
    url = "https://example.com/page"
    with requests_mock.Mocker() as m:
        m.get(url, text=expected_content)

        with pytest.raises(PermissionError):
            download(url, "/root")
