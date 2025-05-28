import os
import re
from urllib.parse import urlparse

import requests


def formate_filename(url: str) -> str:
    parsed = urlparse(url)
    filename = f"{parsed.netloc}{parsed.path}"
    formatted_filename = re.sub(r"[^a-zA-Z0-9]", "-", filename)
    return f"{formatted_filename}.html"


def download(url, dir_path):
    response = requests.get(url)
    response.raise_for_status()

    filename = formate_filename(url)
    filepath = os.path.join(dir_path, filename)

    with open(filepath, "w") as file:
        file.write(response.text)

    return filepath
