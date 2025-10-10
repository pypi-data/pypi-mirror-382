# Sitemap Management Tool

A user-friendly web application for cleaning, updating, and maintaining sitemap files. This tool is designed for SEO specialists, digital marketers, and web administrators who need a simple and reliable way to manage their sitemaps.

## Features

*   **Web-Based UI:** An intuitive interface for uploading files and processing sitemaps without needing command-line skills.
*   **Automated URL Cleaning:** Extracts and cleans URLs from text files.
*   **Bulk URL Operations:** Easily add or remove URLs from your sitemap in bulk.
*   **Rich Reporting:** Get clear, color-coded feedback and test results at each step of the process.
*   **Downloadable Sitemap:** Download the newly generated sitemap file directly from the browser.
*   **Comprehensive Testing:** Includes unit, integration, and end-to-end tests to ensure reliability.

## Getting Started

### Prerequisites

*   Python 3.x
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the Flask server:**
    ```bash
    flask run
    ```
    Or for development mode:
     ```bash
    python app.py
    ```

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000` to access the application.

## How to Use

1.  **Enter a Supplier Name:** This is used to create a dedicated folder for your files.
2.  **Upload the Old Sitemap:** Provide your existing sitemap in `.json` format.
3.  **Upload the Empty URLs File:** Provide a `.txt` file containing the list of URLs to be removed.
4.  **Upload New URLs (Optional):** If you have new URLs to add, provide them in a `.txt` file.
5.  **Process:** Click the "Process Sitemap" button to start the tool.
6.  **View Results:** The application will display a detailed log of the cleaning, removal, and addition processes, along with test results.
7.  **Download:** Once processing is complete, a button will appear to download the new sitemap file.

## Project Structure

```
.
├── app.py                      # Main Flask application
├── requirements.txt            # Project dependencies
├── sitemap_tool/
│   ├── __init__.py
│   ├── main.py                 # Core processing orchestrator
│   ├── logging_config.py       # Rich logging configuration
│   ├── clean_urls.py           # Module for cleaning URLs
│   ├── remove_urls_from_sitemap.py # Module for removing URLs
│   ├── add_urls_to_sitemap.py  # Module for adding URLs
│   ├── test_clean_urls.py      # Tests for URL cleaning
│   ├── test_remove_urls_from_sitemap.py # Tests for URL removal
│   ├── test_add_urls_to_sitemap.py # Tests for URL addition
│   └── tests/
│       ├── test_data/           # Directory for test data
│       ├── test_full_process.py # End-to-end tests
│       └── test_sitemap_integrity.py # Tests for sitemap structure
└── templates/
    └── index.html              # Frontend HTML template
```

## Testing

The project includes a suite of tests to ensure everything is working as expected. To run the tests, you can use Python's `unittest` module.

```bash
# Run all tests
python -m unittest discover sitemap_tool
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.