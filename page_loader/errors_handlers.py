import os
import requests
from requests.exceptions import MissingSchema


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) \
            Gecko/20100101 Firefox/112.0"
}


def request_errors_handler(url):
    try:
        request = requests.get(url, headers=headers,
                               allow_redirects=True, timeout=(3, 7))
        request.raise_for_status()
        return request

    except MissingSchema:
        if '.' not in url and 'localhost' not in url:
            raise MissingSchema("Not correct URL!")
        raise MissingSchema(f"Your url: '{url}', there http or https is \
missing")


def file_errors_handler(path, request):
    try:
        with open(path, "w") as html_file:
            html_file.write(request.text)
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory does not exist \
here! {path}")


def dir_errors_handler(path):
    try:
        os.mkdir(path)

    except FileExistsError:
        path = os.path.split(path)[0]
        raise FileExistsError(f"You have not deleted files from this \
directory ({path}) since the last launch of the program!")
