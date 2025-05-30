import difflib
import os
from urllib.parse import urlparse

import pytest
import requests
from bs4 import BeautifulSoup

from page_loader.page_loader import download, RequestInvalidStatus

HOST = 'ru.hexlet.io'


# Positive: existing url, existing folder
def test_file_download_positive(tmp_path):
    temp = str(tmp_path)
    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    expected_path = os.path.join(temp, 'ru-hexlet-io-courses.html')
    assert file_path == expected_path
    assert os.path.exists(expected_path)


# Positive: existing url, no output provided
def test_download_without_output():
    file_path = download(url='https://ru.hexlet.io/courses')
    expected_path = ('/project/.venv/lib/python3.13/site-packages'
                     '/page_loader/ru-hexlet-io-courses.html')
    assert file_path == expected_path
    expected_assets_dir_path = (os.path.join(
        '/project/.venv/lib/python3.13/site-packages/page_loader',
        'ru-hexlet-io-courses_files'))
    assert os.path.exists(expected_assets_dir_path)


# Positive: Download 2 pages
def test_file_download_two_pages(tmp_path):
    temp = str(tmp_path)
    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    expected_path = os.path.join(temp, 'ru-hexlet-io-courses.html')
    expected_assets_dir_path = os.path.join(temp,
                                            'ru-hexlet-io-courses_files')
    assert file_path == expected_path
    assert os.path.exists(expected_path)
    assert os.path.exists(expected_assets_dir_path)
    file_path_2 = download(url='https://ru.hexlet.io/webinars', output=temp)
    expected_path_2 = os.path.join(temp, 'ru-hexlet-io-webinars.html')
    expected_assets_dir_path = os.path.join(temp,
                                            'ru-hexlet-io-webinars_files')
    assert file_path_2 == expected_path_2
    assert os.path.exists(expected_path_2)
    assert os.path.exists(expected_assets_dir_path)
    assert os.path.exists(expected_path)


# Positive: All expected assets exist
def test_assets_exist(tmp_path):
    temp = str(tmp_path)
    download(url='https://ru.hexlet.io/courses', output=temp)
    required_files = os.listdir(
        f'{os.path.dirname(__file__)}/fixtures/test_all_assets_exist')
    expected_assets_dir_path = os.path.join(temp, 'ru-hexlet-io-courses_files')
    assert os.path.exists(expected_assets_dir_path)
    for file in required_files:
        file_path = os.path.join(expected_assets_dir_path, file)
        assert os.path.exists(file_path)


def test_image_asset_exist(tmp_path):
    temp = str(tmp_path)
    download(
        url='https://en.wikipedia.org/wiki/Robert_II_of_Scotland',
        output=temp)
    expected_assets_dir_path = (
        os.path.join(temp,
                     'en-wikipedia-org-wiki-Robert-II-of-Scotland_files'))
    file_path = (
        os.path.join(expected_assets_dir_path,
        'en-wikipedia-org-static-apple-touch-wikipedia.png'))
    assert os.path.exists(file_path)


# Positive: All assets hrefs changed to local paths
def test_assets_href_change(tmp_path):
    temp = str(tmp_path)
    tags = {"img": "src",
            "link": "href",
            "script": "src"}
    extensions = [".png", ".jpeg"]

    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    with open(file_path, 'r', encoding="utf-8") as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        for tag_type, attribute in tags.items():
            asset_tags = soup.find_all(tag_type)
            for tag in asset_tags:
                if tag.has_attr(attribute):
                    parsed_url = urlparse(tag[attribute])
                    if parsed_url.netloc == HOST or parsed_url.netloc == '':
                        root, file_extension = os.path.splitext(tag[attribute])
                        if file_extension in extensions:
                            assert 'ru-hexlet-io-courses_files' in root
                            assert 'http' not in root


# Compare assets content with etalon
def test_check_asset_content(tmp_path):
    temp = str(tmp_path)
    download(url='https://ru.hexlet.io/courses', output=temp)
    expected_assets_dir_path = os.path.join(temp, 'ru-hexlet-io-courses_files')
    existing_files = set(os.listdir(expected_assets_dir_path))
    for file_ in existing_files:
        root, file_extension = os.path.splitext(file_)
        expected_path = os.path.join(expected_assets_dir_path, file_)
        actual_path = (
            f'{os.path.dirname(__file__)}/fixtures/test_check_asset_content/'
            f'{root}-etalon{file_extension}')
        with (open(expected_path, encoding='UTF-8') as actual_file,
              open(actual_path, encoding='UTF-8') as etalon_file):
            actual_content = actual_file.read()
            etalon_content = etalon_file.read()
            similarity = difflib.SequenceMatcher(None,
                                                 actual_content,
                                                 etalon_content).ratio()
            if similarity < 0.95:
                diff = "\n".join(
                    difflib.unified_diff(
                        etalon_content.splitlines(),
                        actual_content.splitlines(),
                        fromfile='expected',
                        tofile='actual',
                        lineterm=''
                    )
                )
                assert False, (
                    f"Asset {file_} similarity with etalon = {similarity:.2%}."
                    f" Must be >= 0.95.\nDiff:\n{diff}")


# Negative: Unreal URL
def test_unreal_url(tmp_path):
    temp = str(tmp_path)
    with pytest.raises(Exception):
        download(url='https://ru.hexlet.io/lol',
                 output=temp)


# Negative: Unreal output folder
def test_output_path_not_exist():
    unexpected_path = 'файл/'
    with pytest.raises(FileNotFoundError):
        download(url='https://ru.hexlet.io/webinars',
                 output=unexpected_path)


# Negative: Incorrect folder type
def test_incorrect_output_type():
    with pytest.raises(TypeError):
        download(url='https://ru.hexlet.io/webinars',
                 output=1)


def test_local_html_without_requests_get(monkeypatch, tmp_path):
    temp = str(tmp_path)

    def fake_get(url):
        class FakeResponse:
            def __init__(self, text):
                self.text = text

            def ok(self):
                return bool(self)

        path_to_fixture = (
            os.path.join(os.path.dirname(__file__),
                         'fixtures/test_local_html_without_requests_get/'
                         'localhost-blog-about.html'))
        with open(path_to_fixture, 'r', encoding='UTF-8') as site:
            response = site.read()
        return FakeResponse(response)

    monkeypatch.setattr(requests, "get", fake_get)
    download(url='http://localhost/blog/about', output=temp)
