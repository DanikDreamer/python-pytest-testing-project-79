import os
from urllib.parse import urlparse


def filename_from_url(url):
    """
    Generate a filename from a (possibly partial) url
    """
    url = url.lstrip('/')
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '-')
    path_part = parsed_url.path.replace('/', '-').rstrip('-')
    ext = '' if extension(url) else '.html'
    return f'{domain}{path_part}{ext}'


def filename_from_full_url(url):
    """
    Generate a filename from a full url
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('.', '-')
    path_part = parsed_url.path.replace('/', '-').rstrip('-')
    return f'{domain}{path_part}'


def dirname_for_web_assets(content_filename, suffix='files'):
    """
    Generate a directory name for saving web resources based
    on the content filename.
    """
    basename, _ = content_filename.split('.')
    return f'{basename}_{suffix}'


def full_url(url, file_name='index.html'):
    if url == full_domain(url):
        return url

    if not extension(url):
        url = f"{url.rstrip('/')}/{file_name}"

    return url


def base_url(url):
    if not extension(url):
        url = full_url(url)
    url_file_name = file_name(url)
    return url.rstrip(url_file_name)


def scheme(url):
    return urlparse(url).scheme


def domain(url):
    return urlparse(url).netloc


def full_domain(url):
    return f'{scheme(url)}://{domain(url)}'


def extension(url):
    path = urlparse(url).path
    _, extension = os.path.splitext(path)
    return extension[1:]


def file_name(url):
    file_name = os.path.basename(url)
    if file_name == domain(url):
        return ''
    return file_name


def is_absolute_path(url):
    return url.startswith('/')
