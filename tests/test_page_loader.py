import logging
import os
import pathlib
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError

from page_loader.page import download

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


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
    # with pytest.raises(ConnectionError):
    #     download(url, tmp_path)

    with pytest.raises(Exception) as excinfo:
        download(url, tmp_path)
    logger.warning("Raised: %s", repr(excinfo.value))

    dir = list(tmp_path.iterdir())
    logger.info("dir: %s", [*dir])


@pytest.mark.parametrize("status_code", [404, 500])
def test_response_with_error(status_code, requests_mock, tmp_path):
    url = f"https://site.com/{status_code}"
    requests_mock.get(url, status_code=status_code)
    with pytest.raises(HTTPError):
        download(url, tmp_path)

    dir = list(tmp_path.iterdir())
    logger.info("dir: %s", [*dir])


def test_storage_errors(requests_mock, tmp_path):
    url = "https://site.com/blog/about"
    requests_mock.get(url)

    with pytest.raises((OSError, PermissionError)):
        download(url, "/sys")

    with pytest.raises(NotADirectoryError):
        download(url, f"{tmp_path}/site-com-blog-about.html")

    with pytest.raises(NotADirectoryError):
        download(url, f"{tmp_path}/notExistsPath")

    dir = list(tmp_path.iterdir())
    logger.info("dir: %s", [*dir])


def test_page_load(requests_mock, tmp_path):
    url = "https://ru.hexlet.io/courses"
    html_before = read(get_test_data_path("before.html"))
    requests_mock.get(url, text=html_before)

    logger.info("Downloading: %s", url)

    png_data = read(get_test_data_path("logo.png"), binary=True)
    resources_content = {
        "https://ru.hexlet.io/assets/application.css": b"body { background: white; }",
        "https://ru.hexlet.io/assets/professions/python.png": png_data,
        "https://ru.hexlet.io/packs/js/runtime.js": b"console.log('hello');",
        url: html_before.encode("utf-8"),
    }

    expected_asset_filenames = {
        "ru-hexlet-io-assets-application.css",
        "ru-hexlet-io-assets-professions-python.png",
        "ru-hexlet-io-packs-js-runtime.js",
        "ru-hexlet-io-courses.html",
    }

    for resource_url, content in resources_content.items():
        requests_mock.get(resource_url, content=content)

    html_path = download(url, tmp_path)

    logger.info("Saved to: %s", html_path)

    main_html_filename = "ru-hexlet-io-courses.html"
    assets_dirname = "ru-hexlet-io-courses_files"

    assert html_path == os.path.join(tmp_path, main_html_filename)
    assert tmp_path in Path(html_path).parents

    actual_html = read(html_path)
    expected_html = read(get_test_data_path("after.html"))
    assert normalize_html(actual_html) == normalize_html(expected_html)

    assets_dir_path = tmp_path / assets_dirname
    assert (
        assets_dir_path / "ru-hexlet-io-assets-application.css"
    ).read_bytes() == resources_content["https://ru.hexlet.io/assets/application.css"]
    assert (
        assets_dir_path / "ru-hexlet-io-assets-professions-python.png"
    ).read_bytes() == resources_content[
        "https://ru.hexlet.io/assets/professions/python.png"
    ]
    assert (
        assets_dir_path / "ru-hexlet-io-packs-js-runtime.js"
    ).read_bytes() == resources_content["https://ru.hexlet.io/packs/js/runtime.js"]
    assert (assets_dir_path / "ru-hexlet-io-courses.html").read_text() == html_before

    soup = BeautifulSoup(actual_html, "html.parser")

    expected_local_paths_in_html = {
        "link": [
            f"{assets_dirname}/ru-hexlet-io-assets-application.css",
            f"{assets_dirname}/ru-hexlet-io-courses.html",
        ],
        "img": [f"{assets_dirname}/ru-hexlet-io-assets-professions-python.png"],
        "script": [f"{assets_dirname}/ru-hexlet-io-packs-js-runtime.js"],
    }

    found_link_paths = sorted(
        [
            link.get("href")
            for link in soup.find_all("link", href=True)
            if link.get("href").startswith(assets_dirname)
        ]
    )
    assert found_link_paths == sorted(
        expected_local_paths_in_html["link"]
    ), f"Mismatch in local <link> hrefs. Found: {found_link_paths}, Expected: {expected_local_paths_in_html['link']}"

    found_img_paths = sorted(
        [
            img.get("src")
            for img in soup.find_all("img", src=True)
            if img.get("src").startswith(assets_dirname)
        ]
    )
    assert found_img_paths == sorted(
        expected_local_paths_in_html["img"]
    ), f"Mismatch in local <img> srcs. Found: {found_img_paths}, Expected: {expected_local_paths_in_html['img']}"

    found_script_paths = sorted(
        [
            script.get("src")
            for script in soup.find_all("script", src=True)
            if script.get("src").startswith(assets_dirname)
        ]
    )
    assert found_script_paths == sorted(
        expected_local_paths_in_html["script"]
    ), f"Mismatch in local <script> srcs. Found: {found_script_paths}, Expected: {expected_local_paths_in_html['script']}"

    items_in_tmp_path = {item.name for item in tmp_path.iterdir()}
    expected_items_in_tmp_path = {main_html_filename, assets_dirname}
    assert (
        items_in_tmp_path == expected_items_in_tmp_path
    ), f"Unexpected files in tmp_path. Found: {items_in_tmp_path}, Expected: {expected_items_in_tmp_path}"

    items_in_assets_dir = {item.name for item in assets_dir_path.iterdir()}
    assert (
        items_in_assets_dir == expected_asset_filenames
    ), f"Unexpected files in assets_dir. Found: {items_in_assets_dir}, Expected: {expected_asset_filenames}"

    assert requests_mock.called
    assert (
        requests_mock.call_count == 5
    ), f"Expected 5 HTTP requests, but {requests_mock.call_count} were made."

    logger.info("Request history: %s", requests_mock.request_history)
    logger.info("url: %s", requests_mock.request_history[0].url)
    logger.info("method: %s", requests_mock.request_history[0].method)

    dir_content = list(tmp_path.iterdir())
    files_in_assets_dir = list(assets_dir_path.iterdir())
    assert len(files_in_assets_dir) == len(expected_asset_filenames)
    logger.info("dir: %s", [*dir_content])
    logger.info("len asset dir: %s", [*files_in_assets_dir])
