import os
import json
from rich.console import Console
from rich.table import Table
from . import clean_urls, remove_urls_from_sitemap, add_urls_to_sitemap
from .logging_config import setup_logging

log = setup_logging()

def run_tool_full_process(
    supplier_dir_absolute,
    old_sitemap_filename,
    empty_pages_filename,
    new_sitemap_filename,
    new_urls_filename=None
):
    """
    Runs the full sitemap processing tool and generates rich output.
    """
    console = Console(record=True, width=120)

    # Step 1: Clean URLs
    clean_urls.clean_and_extract_urls(
        supplier_dir_absolute,
        empty_pages_filename
    )

    # Step 2: Remove URLs from Sitemap
    remove_urls_from_sitemap.remove_urls(
        supplier_dir_absolute,
        old_sitemap_filename,
        new_sitemap_filename
    )

    # Step 3: Add new URLs if provided
    if new_urls_filename and os.path.exists(os.path.join(supplier_dir_absolute, new_urls_filename)):
        add_urls_to_sitemap.add_urls(
            supplier_dir_absolute,
            new_urls_filename,
            new_sitemap_filename
        )

    # Step 4: Generate final summary table
    summary_table = Table(title="Final Summary", show_header=True, header_style="bold blue")
    summary_table.add_column("Metric", style="dim")
    summary_table.add_column("Count")

    try:
        with open(os.path.join(supplier_dir_absolute, old_sitemap_filename), 'r') as f:
            old_sitemap_data = json.load(f)
            previous_url_count = len(old_sitemap_data.get('startUrl', []))

        with open(os.path.join(supplier_dir_absolute, 'empty-pages-urls.json'), 'r') as f:
            removed_urls_data = json.load(f)
            removed_url_count = len(removed_urls_data.get('urls', []))

        added_url_count = 0
        if new_urls_filename:
            new_urls_json_path = os.path.join(supplier_dir_absolute, 'new-urls.json')
            if os.path.exists(new_urls_json_path):
                with open(new_urls_json_path, 'r') as f:
                    added_urls_data = json.load(f)
                    added_url_count = len(added_urls_data.get('urls', []))

        with open(os.path.join(supplier_dir_absolute, new_sitemap_filename), 'r') as f:
            new_sitemap_data = json.load(f)
            new_total_urls = len(new_sitemap_data.get('startUrl', []))

        summary_table.add_row("Previous Number of URLs", str(previous_url_count))
        summary_table.add_row("Number of URLs Removed", str(removed_url_count))
        summary_table.add_row("Number of URLs Added", str(added_url_count))
        summary_table.add_row("New Total URLs", str(new_total_urls))

        console.print(summary_table)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        console.print(f"[red]Error generating final summary: {e}[/red]")

    return console.export_text()