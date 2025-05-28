import logging
import os
import re
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO)


def formate_filename(url: str) -> str:
    parsed = urlparse(url)
    filename = f"{parsed.netloc}{parsed.path}"
    formatted_filename = re.sub(r"[^a-zA-Z0-9]", "-", filename)
    return f"{formatted_filename}.html"


def download(url, dir_path=os.getcwd()):
    logging.info(f"requested url: {url}")
    logging.info(f"output path: {dir_path}")

    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"{dir_path} is not a directory")

    response = requests.get(url, timeout=(3, 10))
    response.raise_for_status()

    filename = formate_filename(url)
    filepath = os.path.join(dir_path, filename)

    with open(filepath, "w") as file:
        file.write(response.text)

    logging.info(f"write html file: {filepath}")

    return filepath
