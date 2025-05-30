import argparse
import logging
import sys

from page_loader import download

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Page loader utility")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("-o", "--output", help="Directory to save file", default=".")
    args = parser.parse_args()

    try:
        file_path = download(args.url, args.output)
        print(f"Page was downloaded as '{file_path}'")
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
