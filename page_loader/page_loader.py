import logging
import os
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def make_filename(url, extension='html'):
    """Формирует имя файла на основе URL"""
    parsed = urlparse(url)
    raw = parsed.netloc + parsed.path + (f"-{parsed.query}" if parsed.query else "")
    name = re.sub(r"\W+", "-", raw).strip("-")  # Замена недопустимых символов и удаление лишних '-'
    return f"{name}.{extension}"


def get_image_name(img_url):
    """Создает имя для изображения по URL"""
    parsed = urlparse(img_url)
    path, ext = os.path.splitext(parsed.path)
    ext = ext.lower() if ext.lower() in ['.jpg', '.jpeg', '.png'] else '.png'
    return make_filename(parsed.netloc + path, ext[1:])  # без точки


def download_image(img_url, save_path):
    """Скачивает изображение и сохраняет его"""
    logger.info(f"Скачивание изображения: {img_url}")
    response = requests.get(img_url)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(response.content)
    logger.info(f"Изображение сохранено: {save_path}")


def download(url, output_dir=os.getcwd()):
    """Скачивает HTML-страницу и связанные изображения"""
    logger.info(f"Скачивание страницы: {url}")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    base_name = make_filename(url, 'html').replace('.html', '')
    resource_dir = os.path.join(output_dir, f"{base_name}_files")
    os.makedirs(resource_dir, exist_ok=True)

    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if not src:
            continue

        img_url = urljoin(url, src)  # Полный URL к изображению
        img_name = get_image_name(img_url)
        img_path = os.path.join(resource_dir, img_name)

        try:
            download_image(img_url, img_path)
            # Замена ссылки в HTML
            img_tag["src"] = f"{base_name}_files/{img_name}"
        except requests.RequestException as e:
            logger.warning(f"Не удалось скачать изображение {img_url}: {e}")

    # Сохранение обновленного HTML
    html_path = os.path.join(output_dir, f"{base_name}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    logger.info(f"Страница сохранена: {html_path}")
    return html_path
