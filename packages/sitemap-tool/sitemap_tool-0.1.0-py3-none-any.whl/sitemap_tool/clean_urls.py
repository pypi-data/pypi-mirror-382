import re
import json
import os
import argparse
from .logging_config import setup_logging

log = setup_logging()

def clean_and_extract_urls(supplier_directory, empty_pages_filename="empty-pages.txt"):
    """
    Cleans a text file by extracting URLs and saving them to a JSON file
    and overwriting the original text file.
    """
    supplier_base_dir = supplier_directory
    empty_pages_txt_path = os.path.join(supplier_base_dir, empty_pages_filename)
    empty_pages_json_path = os.path.join(supplier_base_dir, "empty-pages-urls.json")

    log.info("[bold]Step 1: Cleaning URLs[/bold]")

    try:
        log.info(f"Reading URLs from: {empty_pages_txt_path}")
        with open(empty_pages_txt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        url_pattern = re.compile(r"https?://[^\s]+")
        extracted_urls = url_pattern.findall(content)
        log.info(f"  - Found {len(extracted_urls)} URLs to clean.")

        log.info(f"Writing cleaned URLs to: {empty_pages_json_path}")
        with open(empty_pages_json_path, 'w', encoding='utf-8') as f:
            json.dump({"urls": extracted_urls}, f, indent=2)

        log.info(f"Overwriting original file with cleaned URLs: {empty_pages_txt_path}")
        temp_file_path = empty_pages_txt_path + ".tmp"
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            for url in extracted_urls:
                f.write(url + '\n')
        os.replace(temp_file_path, empty_pages_txt_path)

        log.info("[green]✓[/green] URL cleaning process completed successfully.")
    except FileNotFoundError:
        log.error(f"[red]✗[/red] Error: The file {empty_pages_txt_path} was not found.")
    except Exception as e:
        log.error(f"[red]✗[/red] An unexpected error occurred during URL cleaning: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="Cleans a text file by extracting URLs.")
    parser.add_argument("supplier_directory", help="The absolute path to the supplier's directory.")
    parser.add_argument("--empty_pages_filename", default="empty-pages.txt", help="The name of the input text file.")
    args = parser.parse_args()

    if not os.path.isdir(args.supplier_directory):
        print(f"Error: Supplier directory not found: {args.supplier_directory}")
        return

    clean_and_extract_urls(args.supplier_directory, args.empty_pages_filename)

if __name__ == '__main__':
    main()