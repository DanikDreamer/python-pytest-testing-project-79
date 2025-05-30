import os
import logging
import pytest
from page_loader import download
from requests.exceptions import HTTPError, MissingSchema, ConnectionError

logging.getLogger('PIL').setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def dir_for_tests(tmp_path):
    directory = tmp_path / "dir"
    directory.mkdir()
    return f"{tmp_path}/dir"


def test_page_loader_not_correct_url(dir_for_tests):
    tmp_path = dir_for_tests
    with pytest.raises(MissingSchema) as error:
        download("not_a_correct_url", tmp_path)
        assert error == 'Not correct URL!'


def test_page_loader_not_correct_url2(dir_for_tests):
    tmp_path = dir_for_tests
    with pytest.raises(ConnectionError) as error:
        download("https://not_a_correct_url.ru", tmp_path)
        assert error == 'Not correct URL!'


def test_page_loader_not_schema(dir_for_tests):
    tmp_path = dir_for_tests
    with pytest.raises(MissingSchema) as error:
        download("google.com", tmp_path)
    assert str(error.value) == "Your url: 'google.com', there http or https \
is missing"


def test_page_loader_error_404(dir_for_tests, requests_mock):
    tmp_path = dir_for_tests
    requests_mock.get("https://google.com/python",
                      text="data", status_code=404, reason='Not Found')

    with pytest.raises(HTTPError) as error:
        download("https://google.com/python", tmp_path)
    assert str(error.value) == '404 Client Error: Not Found for url: \
https://google.com/python'


def test_page_loader_file_exists_error(tmp_path, requests_mock):
    directory = tmp_path / "some-page-com_files"
    directory.mkdir()

    requests_mock.get("https://some_page.com", text="data")
    with pytest.raises(FileExistsError) as error:
        download("https://some_page.com", tmp_path)

    assert str(error.value) == f"You have not deleted files from this \
directory ({tmp_path}) since the last launch of the program!"


def test_page_loader_file_not_found_error(dir_for_tests, requests_mock):
    tmp_path = dir_for_tests
    requests_mock.get("https://some_page.com", text="data")

    with pytest.raises(FileNotFoundError) as error:
        path = os.path.join(tmp_path, "avada_kedavra")
        download("https://some_page.com", path)

    assert str(error.value) == f"Directory does not exist \
here! {tmp_path}/avada_kedavra/some-page-com.html"
