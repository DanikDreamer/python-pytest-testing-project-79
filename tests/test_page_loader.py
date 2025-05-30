import os  # noqa
import logging
import pytest
from page_loader import download


logging.getLogger("PIL").setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.INFO)


def file_fixtures(file):
    file_path = os.path.join(os.getcwd() ,"tests/fixtures", file)
    return file_path

@pytest.fixture
def dir_for_tests(tmp_path):
    directory = tmp_path / "dir"
    directory.mkdir()
    return f"{tmp_path}/dir"


def test_page_loader_check_return_string(dir_for_tests, requests_mock):
    tmp_path = dir_for_tests

    requests_mock.get("https://ru.hexlet.io/courses", text="data")
    file_path = download("https://ru.hexlet.io/courses", tmp_path)

    assert file_path == f"{tmp_path}/ru-hexlet-io-courses.html"


def test_page_loader_check_requests_count(dir_for_tests, requests_mock):
    tmp_path = dir_for_tests

    requests_mock.get("https://some_page.com", text="data")
    download("https://some_page.com", tmp_path)

    assert requests_mock.call_count == 1


def test_page_loader_download_files(dir_for_tests, requests_mock):
    tmp_path = dir_for_tests

    with open(file_fixtures("some-complex-page-com.html")) as main, open(
        file_fixtures(
            "fixtures_for_complex/ru-hexlet-io-assets-professions-python.png"
        ),
        "br",
    ) as image, open(
        file_fixtures("fixtures_for_complex/ru-hexlet-io-assets-application.css")  # noqa E501
    ) as css, open(
        file_fixtures("fixtures_for_complex/ru-hexlet-io-packs-js-runtime.js")
    ) as js:
        requests_mock.get("https://ru.hexlet.io/courses", text=main.read())
        requests_mock.get(
            "https://ru.hexlet.io/assets/application.css", text=css.read()
        )
        requests_mock.get(
            "https://ru.hexlet.io/assets/professions/python.png",
            content=image.read(),
        )
        requests_mock.get("https://ru.hexlet.io/packs/js/runtime.js",
                          text=js.read())

        download("https://ru.hexlet.io/courses", tmp_path)
        directory = os.path.join(tmp_path, "ru-hexlet-io-courses_files")
        for f in os.listdir(directory):
            file_path = os.path.join(directory, f)
            fixture_path = os.path.join(file_fixtures(
                "fixtures_for_complex"), f)

            with open(file_path, "rb") as file, open(
                    fixture_path, "rb") as fixture:
                if f == "ru-hexlet-io-assets-professions-python.png":
                    continue
                assert file.read() == fixture.read()

        main_path = os.path.join(tmp_path, "ru-hexlet-io-courses.html")
    with open(main_path) as main, open(
        file_fixtures("some-complex-page-com-after.html"), "r"
    ) as fixture:
        assert main.read() == fixture.read()
