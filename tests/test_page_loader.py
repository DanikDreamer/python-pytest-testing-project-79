import logging
import os
import tempfile
from pathlib import Path

import pytest
import requests
import requests_mock
from bs4 import BeautifulSoup

from page_loader import download

# Настройка логирования для читаемого вывода
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@pytest.fixture
def temp_dir():
    """Фикстура для создания временной директории"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.mark.parametrize("status_code", [404, 500])
def test_response_errors(temp_dir, status_code):
    """Тестирование обработки ошибок 404 и 500"""
    url = f"https://site.com/error-{status_code}"

    with requests_mock.Mocker() as m:
        m.get(url, status_code=status_code)
        logger.info("Requested URL: %s (Expected error %s)", url, status_code)

        with pytest.raises(requests.exceptions.HTTPError):
            download(url, temp_dir)


@pytest.mark.parametrize(
    "invalid_path, expected_exception",
    [
        ("/notExistsPath", (OSError, FileNotFoundError)),
        ("/sys", PermissionError),
    ],
)
def test_storage_errors(invalid_path, expected_exception):
    """Тестирование ошибок при сохранении"""
    url = "https://site.com/blog/about"

    with requests_mock.Mocker() as m:
        m.get(url, text="<html></html>")

        with pytest.raises(expected_exception):
            download(url, invalid_path)


def test_download(temp_dir):
    """Тестирование скачивания страницы"""
    url = "https://ru.hexlet.io/courses"
    test_page_text = "<html><body>Test Page</body></html>"
    expected_filename = os.path.join(temp_dir, "ru-hexlet-io-courses.html")
    expected_html = BeautifulSoup(test_page_text, "html.parser").prettify()

    with requests_mock.Mocker() as m:
        m.get(url, text=test_page_text)  # Подмена запроса

        logger.info("Downloading: %s", url)
        file_path = download(url, temp_dir)
        logger.info("Saved to: %s", file_path)

        # Проверка, что файл создан и корректен
        assert os.path.exists(file_path)
        assert file_path == expected_filename

        # Проверка содержимого файла
        with open(file_path, encoding="utf-8") as file:
            assert file.read() == expected_html

        # Проверка, что requests.get(url) был вызван ОДИН раз
        assert len(m.request_history) == 1
        # Проверка, что запрос был сделан по нужному URL
        assert m.request_history[0].url == url
        # Проверка, что это именно GET-запрос
        assert m.request_history[0].method == "GET"


def test_download_with_images(tmp_path):
    """Проверка скачивания изображений и замены ссылок"""
    url = "https://ru.hexlet.io/courses"
    html_content = """
    <html>
      <body>
        <img src="/assets/professions/python.png" />
      </body>
    </html>
    """
    img_url = "https://ru.hexlet.io/assets/professions/python.png"
    # Загружаем реальную картинку из fixtures
    real_image_path = Path(__file__).parent / "fixtures/python.png"
    img_content = real_image_path.read_bytes()

    expected_img_filename = "ru-hexlet-io-assets-professions-python.png"
    expected_img_path = os.path.join(
        tmp_path, "ru-hexlet-io-courses_files", expected_img_filename
    )
    expected_html_path = os.path.join(tmp_path, "ru-hexlet-io-courses.html")

    with requests_mock.Mocker() as m:
        m.get(url, text=html_content)
        m.get(img_url, content=img_content)

        file_path = download(url, tmp_path)

        logger.info(f"Проверка: HTML сохранён в {expected_html_path}")
        assert os.path.exists(expected_html_path)
        assert file_path == expected_html_path

        logger.info(f"Проверка: изображение сохранено в {expected_img_path}")
        assert os.path.exists(expected_img_path)

        logger.info("Проверка: файл совпадает с оригиналом")
        downloaded_image = Path(expected_img_path).read_bytes()
        assert downloaded_image == img_content

        with open(expected_html_path, encoding="utf-8") as file:
            html = file.read()
            logger.info("Проверка: заменена ли ссылка на локальное изображение в HTML")
            assert f'src="ru-hexlet-io-courses_files/{expected_img_filename}"' in html
