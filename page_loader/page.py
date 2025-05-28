import logging
import os
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


def formate_filename(url: str) -> str:
    parsed = urlparse(url)
    path = f"{parsed.netloc}{parsed.path}"
    name, ext = os.path.splitext(path)
    formatted_name = re.sub(r"[^a-zA-Z0-9]", "-", name)
    if not ext and not path.endswith("/"):
        ext = ".html"
    return f"{formatted_name}{ext}"


def is_local(src_url, page_url):
    src_parsed = urlparse(urljoin(page_url, src_url))
    page_parsed = urlparse(page_url)
    return src_parsed.netloc == "" or src_parsed.netloc == page_parsed.netloc


def download(url, dir_path=os.getcwd()):
    logging.info(f"requested url: {url}")
    logging.info(f"output path: {dir_path}")

    response = requests.get(url, timeout=(3, 10))
    response.raise_for_status()

    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"{dir_path} is not a directory")
    filename = formate_filename(url)
    html_path = os.path.join(dir_path, filename)

    with open(html_path, "w") as file:
        file.write(response.text)
    logging.info(f"write html file: {html_path}")

    assets_dirname = os.path.splitext(filename)[0] + "_files"
    assets_dir = os.path.join(dir_path, assets_dirname)
    os.makedirs(assets_dir, exist_ok=True)
    logging.info(f"create directory for assets: {assets_dir}")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup.find_all("img"):
        src = tag.get("src")
        if not src or not is_local(src, url):
            continue

        asset_url = urljoin(url, src)
        asset_filename = formate_filename(asset_url)
        asset_path = os.path.join(assets_dir, asset_filename)

        asset_response = requests.get(asset_url, timeout=(3, 10))
        asset_response.raise_for_status()

        with open(asset_path, "wb") as asset_file:
            asset_file.write(asset_response.content)

        tag["src"] = os.path.join(assets_dirname, asset_filename)

    with open(html_path, "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    return html_path
