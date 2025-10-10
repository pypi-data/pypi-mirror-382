import json
import os
import argparse
from .logging_config import setup_logging

log = setup_logging()

def add_urls(supplier_directory, urls_to_add_filename, target_sitemap_filename):
    """
    Adds URLs from a text file to the 'startUrl' section of a sitemap JSON file.
    """
    log.info("[bold]Step 3: Adding URLs to Sitemap[/bold]")

    supplier_base_dir = supplier_directory
    urls_to_add_txt_path = os.path.join(supplier_base_dir, urls_to_add_filename)
    urls_to_add_json_path = os.path.join(supplier_base_dir, "new-urls.json")
    target_sitemap_path = os.path.join(supplier_base_dir, target_sitemap_filename)

    try:
        log.info(f"Loading URLs from: {urls_to_add_txt_path}")
        with open(urls_to_add_txt_path, 'r', encoding='utf-8') as f:
            urls_from_txt = [line.strip() for line in f if line.strip()]
        log.info(f"  - Found {len(urls_from_txt)} URLs to add.")

        log.info(f"Saving URLs to be added to: {urls_to_add_json_path}")
        with open(urls_to_add_json_path, 'w', encoding='utf-8') as f:
            json.dump({"urls": urls_from_txt}, f, indent=2)


        log.info(f"Loading target sitemap: {target_sitemap_path}")
        with open(target_sitemap_path, 'r', encoding='utf-8') as f:
            sitemap_data = json.load(f)

        if "startUrl" not in sitemap_data or not isinstance(sitemap_data["startUrl"], list):
            sitemap_data["startUrl"] = []
            log.warning("  - 'startUrl' key not found or not a list. Initializing as empty list.")

        existing_urls_set = set(sitemap_data["startUrl"])
        added_count = 0
        for url in urls_from_txt:
            if url not in existing_urls_set:
                sitemap_data["startUrl"].append(url)
                existing_urls_set.add(url)
                added_count += 1

        log.info(f"  - Added {added_count} new URLs.")
        log.info(f"  - New total sitemap URL count: {len(sitemap_data['startUrl'])}")

        log.info(f"Saving updated sitemap to: {target_sitemap_path}")
        with open(target_sitemap_path, 'w', encoding='utf-8') as f:
            json.dump(sitemap_data, f, indent=2)

        log.info("[green]✓[/green] URL addition process completed successfully.")
    except FileNotFoundError as e:
        log.error(f"[red]✗[/red] Error: Required file not found: {e.filename}.")
    except json.JSONDecodeError as e:
        log.error(f"[red]✗[/red] Error: Could not decode JSON from a file. Check JSON syntax: {e}")
    except Exception as e:
        log.error(f"[red]✗[/red] An unexpected error occurred during URL addition: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="Adds URLs from a text file to a sitemap JSON file.")
    parser.add_argument("supplier_directory", help="The absolute path to the supplier's directory.")
    parser.add_argument("--urls_to_add_filename", required=True, help="The filename of the text file containing URLs to add.")
    parser.add_argument("--target_sitemap_filename", required=True, help="The filename of the sitemap JSON file to be updated.")
    args = parser.parse_args()

    if not os.path.isdir(args.supplier_directory):
        print(f"Error: Supplier directory not found: {args.supplier_directory}")
        return

    add_urls(
        args.supplier_directory,
        args.urls_to_add_filename,
        args.target_sitemap_filename
    )

if __name__ == '__main__':
    main()