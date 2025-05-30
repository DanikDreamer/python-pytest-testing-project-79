import os
import pathlib
import tempfile
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError

from page_loader import download


def read(file_path, binary=False):
    mode = "rb" if binary else "r"
    with open(file_path, mode) as f:
        return f.read()


def get_test_data_path(filename):
    return pathlib.Path(__file__).parent / "test_data" / filename


def normalize_html(html_str):
    return BeautifulSoup(html_str, "html.parser").prettify()


def test_invalid_url(tmp_path):
    with pytest.raises(ValueError):
        download("not-a-url", tmp_path)


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

    with pytest.raises((OSError, PermissionError)):
        download(url, "/sys")

    with pytest.raises(NotADirectoryError):
        download(url, f"{tmp_path}/site-com-blog-about.html")

    with pytest.raises(NotADirectoryError):
        download(url, f"{tmp_path}/notExistsPath")


def test_page_load(requests_mock, tmp_path):
    url = "https://ru.hexlet.io/courses"
    html_before = read(get_test_data_path("before.html"))
    requests_mock.get(url, text=html_before)

    png_data = read(get_test_data_path("logo.png"), binary=True)
    resources = {
        "https://ru.hexlet.io/assets/application.css": b"body { background: white; }",
        "https://ru.hexlet.io/assets/professions/python.png": png_data,
        "https://ru.hexlet.io/packs/js/runtime.js": b"console.log('hello');",
    }

    for resource_url, content in resources.items():
        requests_mock.get(resource_url, content=content)

    html_path = download(url, tmp_path)
    actual_html = read(html_path)
    expected_html = read(get_test_data_path("after.html"))

    assert html_path == f"{tmp_path}/ru-hexlet-io-courses.html"
    assert tmp_path in Path(html_path).parents
    assert normalize_html(actual_html) == normalize_html(expected_html)

    assets_dir = tmp_path / "ru-hexlet-io-courses_files"
    assert (
        assets_dir / "ru-hexlet-io-assets-application.css"
    ).read_bytes() == resources["https://ru.hexlet.io/assets/application.css"]
    assert (
        assets_dir / "ru-hexlet-io-assets-professions-python.png"
    ).read_bytes() == resources["https://ru.hexlet.io/assets/professions/python.png"]
    assert (assets_dir / "ru-hexlet-io-packs-js-runtime.js").read_bytes() == resources[
        "https://ru.hexlet.io/packs/js/runtime.js"
    ]
    assert (assets_dir / "ru-hexlet-io-courses.html").read_text() == html_before

    assert requests_mock.called
    assert requests_mock.call_count == 5

    files = list(assets_dir.iterdir())
    assert len(files) == 4
