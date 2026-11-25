# Professional Web Scraping and Data Analysis Pipeline

This project builds a professional, resilient web scraper and data analysis pipeline using Python. It targets [Books to Scrape](http://books.toscrape.com/), crawling catalog listings, category pages, handling pagination, traversing detail pages, cleaning the scraped data, and producing key analytical insights and charts.

## Project Structure
```
├── scraper/
│   ├── __init__.py      # Package initialization
│   ├── client.py        # Resilient HTTP request helper with rotating User-Agents and rate limiting
│   ├── parser.py        # BeautifulSoup parsers for indices, paginations, and details
│   └── pipeline.py      # Orchestrator for crawler stages
├── analyzer.py          # Data cleaning, metric calculation, and visualization generator
├── main.py              # CLI entry point to coordinate scraping, cleaning, and analysis
├── requirements.txt     # Third-party dependency definitions
└── README.md            # Project documentation (this file)
```

## Features
1. **Resiliency**: Custom client uses `urllib3.util.Retry` adapters to handle temporary network errors (500, 502, 503, 504) and rotational User-Agent headers.
2. **Politeness**: Built-in polite delay intervals to respect target server bandwidth constraints.
3. **Robust Parsers**: Extracts detailed attributes (UPC, title, category, descriptions, stock availability, star ratings).
4. **Data Cleaning & Analytics**: Converts dirty text strings into clean numeric variables (floats/integers) and outputs a detailed descriptive statistics text file.
5. **Aesthetic Visualizations**: Renders publication-quality seaborn plots showing rating distributions, pricing histograms, and average prices across categories.

## Getting Started

### Prerequisites
Make sure you have Python 3.10+ installed.

### Installation
Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Pipeline
You can run the full pipeline or limit it to quickly verify correctness.

#### Run with a limit of 30 books (recommended for quick testing):
```bash
python main.py --limit-books 30
```

#### Run with a page limit (e.g. scrape first 3 pages of books):
```bash
python main.py --max-pages 3
```

#### Run full scrape (scrapes all 1000 books across 50 pages):
```bash
python main.py
```

## Outputs
All outputs are generated automatically:
- **Raw Data**: `data/raw_books.json`
- **Cleaned Dataset**: `exports/cleaned_books.csv`
- **Text Summary Report**: `exports/analytical_report.txt`
- **Rating Distribution Chart**: `exports/rating_distribution.png`
- **Price Distribution Chart**: `exports/price_distribution.png`
- **Average Price by Category**: `exports/average_price_by_category.png`
