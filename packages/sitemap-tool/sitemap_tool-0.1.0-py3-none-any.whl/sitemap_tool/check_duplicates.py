import json
import os

# Define the path to the sitemap file
sitemap_path = r"C:\Users\Simon\OneDrive\Documents\Clients\Naken\Product update issues\sitemaps\Andrew Martin\new_andrew_martin_sitemap.json"

def check_for_duplicates(sitemap_file_path):
    try:
        with open(sitemap_file_path, 'r', encoding='utf-8') as f:
            sitemap_data = json.load(f)

        if "startUrl" in sitemap_data and isinstance(sitemap_data["startUrl"], list):
            urls = sitemap_data["startUrl"]
            unique_urls = set(urls)

            if len(urls) != len(unique_urls):
                print(f"Duplicates found in {sitemap_file_path}!")
                # Optionally, print the duplicate URLs
                duplicates = [url for url in urls if urls.count(url) > 1]
                print("Duplicate URLs:")
                for url in set(duplicates): # Print unique duplicates
                    print(f"- {url}")
                print(f"Total URLs: {len(urls)}")
                print(f"Unique URLs: {len(unique_urls)}")
            else:
                print(f"No duplicates found in {sitemap_file_path}.")
                print(f"Total URLs: {len(urls)}")
        else:
            print(f"'startUrl' key not found or is not a list in {sitemap_file_path}.")

    except FileNotFoundError:
        print(f"Error: Sitemap file not found at {sitemap_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {sitemap_file_path}. Check file integrity.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    check_for_duplicates(sitemap_path)
