import os

from urllib.parse import urlparse
from bs4 import BeautifulSoup
import validators
from page_loader.errors_handlers import request_errors_handler
from page_loader.errors_handlers import file_errors_handler
from page_loader.errors_handlers import dir_errors_handler


def url_to_filename(url: str, type=".html"):
    new_url = url.replace("https://", "").replace("http://", "")
    result = ""
    for char in new_url:
        if char.isalnum():
            result += char
        else:
            result += "-"

    return result + type


def url_validator(link, hostname, scheme):
    if not validators.url(link):
        if link[0] != "/":
            link = f"/{link}"
        link = f"{hostname}{link}"

    if link[:4] != "http":
        link = f"{scheme}://{link}"
    return link


def match_obect_attrs(attrs):
    if 'href' in attrs:
        obj_download_tag = "href"
    elif 'src' in attrs:
        obj_download_tag = "src"
    else:
        obj_download_tag = ''
    return obj_download_tag


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) \
            Gecko/20100101 Firefox/112.0"
}


def get_images(request_text, path, new_dir_name, hostname, scheme):
    soup = BeautifulSoup(request_text, "html.parser")
    objects = soup.find_all(["img", "link", "script"])

    for object in objects:
        obj_download_tag = match_obect_attrs(object.attrs)
        if not obj_download_tag:
            continue

        obj_link = object.get(obj_download_tag)
        obj_link = url_validator(obj_link, hostname, scheme)
        if urlparse(obj_link).hostname != hostname:
            continue
        image = request_errors_handler(obj_link).content

        splited_link = os.path.splitext(obj_link)
        if splited_link[-1] == "":
            img_url, type = splited_link
            type = ".html"
        else:
            img_url, type = os.path.splitext(obj_link)

        filename = url_to_filename(img_url, type)
        new_file_path = os.path.join(path, filename)

        with open(new_file_path, "wb") as file:
            file.write(image)

        relative_path = os.path.join(new_dir_name, filename)
        object.attrs[obj_download_tag] = relative_path
    return soup


def download(url: str, path: str = os.getcwd()) -> str:
    print(f"requested url: {url}")
    absoulute_path = os.path.abspath(path)
    print(f"output path: {absoulute_path}")

    request = request_errors_handler(url)

    new_html_file_name = url_to_filename(url)
    new_html_path = os.path.join(path, new_html_file_name)

    new_html_absolue_path = os.path.abspath(new_html_path)
    print(f"write html file: {new_html_absolue_path}")

    file_errors_handler(new_html_absolue_path, request)

    new_dir_path = f"{new_html_path[:-5]}_files"
    new_dir_name = os.path.split(new_dir_path)[1]
    new_dir_absolute_path = os.path.abspath(new_dir_path)
    print(f"create a directory for assets: {new_dir_absolute_path}")

    dir_errors_handler(new_dir_absolute_path)

    with open(new_html_path, "r+", encoding="utf-8") as file:
        scheme = urlparse(url).scheme
        hostname = urlparse(url).hostname
        soup = get_images(file.read(), new_dir_path, new_dir_name,
                          hostname, scheme)
        file.seek(0)
        file.write(str(soup.prettify()))

    return new_html_path

