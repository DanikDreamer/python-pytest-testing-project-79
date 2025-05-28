import argparse
import sys

from page_loader.page import download


def main():
    parser = argparse.ArgumentParser(description="Page loader utility")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("-o", "--output", help="Directory to save file", default=".")
    args = parser.parse_args()

    try:
        file_path = download(args.url, args.output)
        print(f"Page was downloaded as '{file_path}'")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit()


if __name__ == "__main__":
    main()
