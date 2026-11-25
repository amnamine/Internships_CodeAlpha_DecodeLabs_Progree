import os
import json
import time
import argparse
import logging

from scraper import ScraperPipeline
from analyzer import DataAnalyzer

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("main")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Professional Web Scraping and Analytics Pipeline - Books to Scrape"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum catalog pages to scan (default: all)"
    )
    parser.add_argument(
        "--limit-books",
        type=int,
        default=None,
        help="Maximum books to scrape detail data for (default: all)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Polite delay between HTTP requests in seconds (default: 0.1)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory to save raw crawled data (default: data)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="exports",
        help="Directory to export cleaned datasets and visualizations (default: exports)"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    start_time = time.time()
    
    # Create required directories
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    
    raw_data_file = os.path.join(args.data_dir, "raw_books.json")
    
    # Step 1: Execute scraping
    logger.info("=== STEP 1: WEB SCRAPING ===")
    pipeline = ScraperPipeline(delay=args.delay)
    
    try:
        scraped_data = pipeline.run(
            max_pages=args.max_pages, 
            limit_books=args.limit_books
        )
        
        # Save raw crawled data
        with open(raw_data_file, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=4, ensure_ascii=False)
        logger.info(f"Raw scraped data successfully stored in {raw_data_file}")
        
    except Exception as e:
        logger.exception(f"Scraping phase failed: {e}")
        return

    # Step 2: Data Cleaning, Stats & Visualization
    logger.info("=== STEP 2: DATA CLEANING & ANALYTICS ===")
    try:
        analyzer = DataAnalyzer(
            raw_data_path=raw_data_file,
            output_dir=args.output_dir
        )
        
        # Load and clean dataset
        cleaned_df = analyzer.load_and_clean()
        if cleaned_df.empty:
            logger.error("No data extracted. Skipping analytics and visual report generation.")
            return
            
        # Generate summary stats report
        report_text = analyzer.generate_report()
        print("\n" + report_text + "\n")
        
        # Generate visual charts
        analyzer.generate_visuals()
        
    except Exception as e:
        logger.exception(f"Analytics and visualization phase failed: {e}")
        return

    elapsed_time = time.time() - start_time
    logger.info(f"Pipeline executed successfully in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
