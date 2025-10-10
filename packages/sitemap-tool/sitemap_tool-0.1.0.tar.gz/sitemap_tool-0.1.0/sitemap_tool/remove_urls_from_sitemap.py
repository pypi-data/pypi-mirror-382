import json
import os
import argparse
from .logging_config import setup_logging

log = setup_logging()

def remove_urls(supplier_directory, original_sitemap_filename, new_sitemap_filename, urls_to_remove_filename="empty-pages-urls.json"):
    """
    Removes specified URLs from a sitemap JSON file and saves the result to a new sitemap JSON file.
    """
    log.info("[bold]Step 2: Removing URLs from Sitemap[/bold]")

    supplier_base_dir = supplier_directory
    original_sitemap_path = os.path.join(supplier_base_dir, original_sitemap_filename)
    urls_to_remove_path = os.path.join(supplier_base_dir, urls_to_remove_filename)
    new_sitemap_path = os.path.join(supplier_base_dir, new_sitemap_filename)

    try:
        log.info(f"Loading original sitemap: {original_sitemap_path}")
        with open(original_sitemap_path, 'r', encoding='utf-8') as f:
            sitemap_data = json.load(f)

        log.info(f"Loading URLs to remove: {urls_to_remove_path}")
        with open(urls_to_remove_path, 'r', encoding='utf-8') as f:
            urls_to_remove_data = json.load(f)
            urls_to_remove_set = set(urls_to_remove_data.get("urls", []))
        log.info(f"  - Found {len(urls_to_remove_set)} URLs to remove.")

        if "startUrl" in sitemap_data and isinstance(sitemap_data["startUrl"], list):
            original_start_urls_count = len(sitemap_data["startUrl"])
            log.info(f"  - Original sitemap URL count: {original_start_urls_count}")

            new_start_urls = [url for url in sitemap_data["startUrl"] if url not in urls_to_remove_set]
            removed_count = original_start_urls_count - len(new_start_urls)

            sitemap_data["startUrl"] = new_start_urls
            log.info(f"  - Removed {removed_count} URLs.")
            log.info(f"  - New sitemap URL count: {len(sitemap_data['startUrl'])}")
        else:
            log.warning("  - 'startUrl' key not found or is not a list. No URLs removed.")

        log.info(f"Saving new sitemap to: {new_sitemap_path}")
        with open(new_sitemap_path, 'w', encoding='utf-8') as f:
            json.dump(sitemap_data, f, indent=2)

        log.info("[green]✓[/green] URL removal process completed successfully.")
    except FileNotFoundError as e:
        log.error(f"[red]✗[/red] Error: Required file not found: {e.filename}.")
    except json.JSONDecodeError as e:
        log.error(f"[red]✗[/red] Error: Could not decode JSON from a file. Check JSON syntax: {e}")
    except Exception as e:
        log.error(f"[red]✗[/red] An unexpected error occurred during URL removal: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="Removes specified URLs from a sitemap JSON file.")
    parser.add_argument("supplier_directory", help="The absolute path to the supplier's directory.")
    parser.add_argument("--original_sitemap_filename", required=True, help="The filename of the original sitemap JSON.")
    parser.add_argument("--urls_to_remove_filename", default="empty-pages-urls.json", help="The filename of the JSON file containing URLs to remove.")
    parser.add_argument("--new_sitemap_filename", required=True, help="The filename for the new sitemap JSON.")
    args = parser.parse_args()

    if not os.path.isdir(args.supplier_directory):
        print(f"Error: Supplier directory not found: {args.supplier_directory}")
        return

    remove_urls(
        args.supplier_directory,
        args.original_sitemap_filename,
        args.new_sitemap_filename,
        args.urls_to_remove_filename
    )

if __name__ == '__main__':
    main()