import argparse
import logging
import sys
from page_loader.page_loader import download
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)


def main():
    logging.basicConfig(filename='page_loader.log', level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Page loader Hexlet"
    )
    parser.add_argument('-o', '--output', help='output directory ')
    parser.add_argument('url', help='URL')

    args = parser.parse_args()
    logger.info('page_loader started')
    logger.debug(f'Args from the user: {args}')
    try:
        if args.output:
            file_path = download(url=args.url, output=args.output)
        else:
            file_path = download(url=args.url)
        logger.info(f'page_loader finished. File path: {file_path}')
        print(f'Path to downloaded page: {file_path}')
        return 0
    except Exception as e:
        logger.info(msg=f"Some error occurred during run: {e}")
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

