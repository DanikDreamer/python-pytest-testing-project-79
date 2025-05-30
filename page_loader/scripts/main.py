import argparse
from page_loader.download_manager import DownloadManager
from page_loader.exceptions.network_exceptions import HttpError, RequestError
from page_loader.exceptions.io_exceptions import SaveError, DirectoryError
import logging
import os
import sys
import time


def parse_args():
    parser = argparse.ArgumentParser(description='Web page downloader')
    parser.add_argument('url', metavar='url')
    parser.add_argument('-o', '--output', help='output directory ')
    return parser.parse_args()


def setup_logging():
    log_format = '%(levelname)s:root:%(message)s'

    info_logger = logging.getLogger('info_logger')
    info_logger.setLevel(logging.INFO)
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setFormatter(logging.Formatter(log_format))
    info_logger.addHandler(info_handler)

    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setFormatter(logging.Formatter(log_format))
    error_logger.addHandler(error_handler)


def log_arguments(logger, args):
    logger.info(f'requested url: {args.url}')
    logger.info(f'output path: {args.output}')


def log_download_info(logger, download_manager):
    path_to_save_page_content = download_manager.assets_dir
    assets_dir = download_manager.assets_dir
    logger.info(f'write html file: {path_to_save_page_content}')
    logger.info(f'create directory for assets: {assets_dir}')


def handle_result(result_path, elapsed_time):
    if result_path:
        print(f'Page was downloaded as \'{result_path}\'')
        print(f'Elapsed time: {elapsed_time:.2f} seconds')
        sys.exit(os.EX_OK)


def download(info_logger, error_logger, args):     # noqa: C901
    try:
        start_time = time.time()
        download_manager = DownloadManager(args.url, args.output)
        result_path = download_manager.download()
        log_download_info(info_logger, download_manager)
        elapsed_time = time.time() - start_time
        handle_result(result_path, elapsed_time)

    except HttpError as e:
        error_logger.error(e)
        sys.exit(os.EX_PROTOCOL)

    except RequestError as e:
        error_logger.error(e)
        sys.exit(os.EX_UNAVAILABLE)

    except SaveError as e:
        error_logger.error(e)
        sys.exit(os.EX_OSFILE)

    except DirectoryError as e:
        error_logger.error(e)
        sys.exit(os.EX_IOERR)

    except Exception as e:
        error_logger.error(f'Some ubexpected error:\n{e}')
        sys.exit(os.EX_SOFTWARE)


def main():
    args = parse_args()
    setup_logging()
    info_logger = logging.getLogger('info_logger')
    error_logger = logging.getLogger('error_logger')

    log_arguments(info_logger, args)
    download(info_logger, error_logger, args)


if __name__ == '__main__':
    main()
