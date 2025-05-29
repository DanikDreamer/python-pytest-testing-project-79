import os
import pathlib
from urllib.parse import urljoin, urlparse

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

    with pytest.raises(OSError):
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
    assert (assets_dir / "ru-hexlet-io-courses.html").exists()
    assert "ru-hexlet-io-assets-application.css" in actual_html
    assert 'href="assets/application.css"' not in actual_html

    soup = BeautifulSoup(actual_html, "html.parser")

    for tag in soup.find_all(["link", "script", "img"]):
        attr = "src" if tag.name in ["img", "script"] else "href"
        value = tag.get(attr)
        assert value is not None, f"{tag} missing {attr}"

        parsed = urlparse(value)

        if parsed.scheme in ("http", "https"):
            continue

        assert value.startswith("ru-hexlet-io-courses_files/")
