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


def test_download_returns_correct_path(requests_mock, tmp_path):
    """Check that download returns the correct file path."""
    url = "https://site.com/page"
    html = "<html></html>"
    requests_mock.get(url, text=html)
    result_path = download(url, tmp_path)
    assert os.path.isfile(result_path)
    assert result_path.endswith(".html")


def test_assets_dir_created(requests_mock, tmp_path):
    """Check that assets directory is created and is a directory."""
    url = "https://site.com/page"
    html = '<html><img src="/img.png"></html>'
    requests_mock.get(url, text=html)
    requests_mock.get("https://site.com/img.png", content=b"imgdata")
    download(url, tmp_path)
    assets_dir = tmp_path / "site-com-page_files"
    assert assets_dir.exists()
    assert assets_dir.is_dir()


def test_external_resources_not_downloaded(requests_mock, tmp_path):
    """Check that external resources are not downloaded or replaced."""
    url = "https://site.com/page"
    html = '<html><img src="https://external.com/img.png"></html>'
    requests_mock.get(url, text=html)
    html_path = download(url, tmp_path)
    with open(html_path) as f:
        content = f.read()
    assert "external.com/img.png" in content  # Should not be replaced


def test_relative_links_handling(requests_mock, tmp_path):
    """Check that relative links are resolved and downloaded."""
    url = "https://site.com/page"
    html = '<html><img src="img.png"></html>'
    requests_mock.get(url, text=html)
    requests_mock.get("https://site.com/img.png", content=b"imgdata")
    download(url, tmp_path)
    assets_dir = tmp_path / "site-com-page_files"
    assert (assets_dir / "site-com-img.png").exists()


def test_download_overwrites_existing_files(requests_mock, tmp_path):
    """Check that download overwrites existing files (idempotency)."""
    url = "https://site.com/page"
    html = "<html></html>"
    requests_mock.get(url, text=html)
    html_path = download(url, tmp_path)
    with open(html_path, "w") as f:
        f.write("old content")
    # Call download again, should overwrite
    requests_mock.get(url, text=html)
    html_path2 = download(url, tmp_path)
    with open(html_path2) as f:
        assert f.read() == normalize_html("<html></html>")


def test_download_invalid_url(requests_mock, tmp_path):
    """Check that download raises for invalid URL."""
    url = "not a url"
    with pytest.raises(Exception):
        download(url, tmp_path)


def test_download_handles_empty_html(requests_mock, tmp_path):
    """Check that download works with empty HTML."""
    url = "https://site.com/page"
    requests_mock.get(url, text="")
    html_path = download(url, tmp_path)
    assert os.path.isfile(html_path)
    with open(html_path) as f:
        assert f.read() == ""


def test_download_handles_no_assets(requests_mock, tmp_path):
    """Check that download works if there are no assets."""
    url = "https://site.com/page"
    html = "<html><body>No assets here</body></html>"
    requests_mock.get(url, text=html)
    html_path = download(url, tmp_path)
    assets_dir = tmp_path / "site-com-page_files"
    assert assets_dir.exists()
    assert list(assets_dir.iterdir()) == []


def test_download_asset_link_variants(requests_mock, tmp_path):
    """Check that download handles <link> with rel=stylesheet and others."""
    url = "https://site.com/page"
    html = """
    <html>
        <head>
        <link rel="stylesheet" href="/style.css">
        <link rel="icon" href="/favicon.ico">
        </head>
    </html>
    """
    requests_mock.get(url, text=html)
    requests_mock.get("https://site.com/style.css", content=b"css")
    requests_mock.get("https://site.com/favicon.ico", content=b"ico")
    download(url, tmp_path)
    assets_dir = tmp_path / "site-com-page_files"
    assert (assets_dir / "site-com-style.css").exists()
    assert (assets_dir / "site-com-favicon.ico").exists()
