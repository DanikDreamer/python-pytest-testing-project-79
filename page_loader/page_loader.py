from .download_manager import DownloadManager


def download(url, path=None):
    path = path or ''
    page_loader = DownloadManager(url, path)
    return page_loader.download()
