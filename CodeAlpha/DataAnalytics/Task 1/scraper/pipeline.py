import logging
from .client import ScrapeClient
from .parser import BookParser

logger = logging.getLogger(__name__)

class ScraperPipeline:
    """
    Coordinates the web scraping flow: page traversal, pagination,
    extracting book detail URLs, and scraping individual book detail pages.
    """
    def __init__(self, delay: float = 0.2, max_retries: int = 3):
        self.client = ScrapeClient(delay=delay, max_retries=max_retries)
        self.base_url = "http://books.toscrape.com/"

    def run(self, max_pages: int = None, limit_books: int = None) -> list[dict]:
        """
        Runs the scraper.
        :param max_pages: Maximum number of catalog pages to traverse (None for all).
        :param limit_books: Maximum number of books to scrape in total (None for all).
        """
        logger.info("Starting web scraper pipeline...")
        book_urls = []
        current_url = self.base_url
        page_count = 0
        
        # Phase 1: Collect book detail URLs
        while current_url:
            page_count += 1
            if max_pages and page_count > max_pages:
                logger.info(f"Reached page limit of {max_pages}. Stopping list traversal.")
                break
                
            logger.info(f"Scanning page {page_count}: {current_url}")
            try:
                response = self.client.get(current_url)
                # Parse book links from the current page
                links = BookParser.parse_book_list(response.text, current_url)
                book_urls.extend(links)
                logger.info(f"Found {len(links)} books on page {page_count}. Total collected: {len(book_urls)}.")
                
                # Check for limit
                if limit_books and len(book_urls) >= limit_books:
                    book_urls = book_urls[:limit_books]
                    logger.info(f"Reached book collection limit of {limit_books}.")
                    break
                    
                # Find the next page
                current_url = BookParser.parse_next_page(response.text, current_url)
            except Exception as e:
                logger.error(f"Error while scanning listing page {current_url}: {e}")
                break
        
        logger.info(f"Collected {len(book_urls)} book URLs in total. Proceeding to scrape details...")
        
        # Phase 2: Scrape book details
        books_data = []
        for idx, url in enumerate(book_urls, 1):
            if limit_books and idx > limit_books:
                break
                
            logger.info(f"Scraping book {idx}/{len(book_urls)}: {url}")
            try:
                response = self.client.get(url)
                details = BookParser.parse_book_detail(response.text, url)
                books_data.append(details)
            except Exception as e:
                logger.error(f"Failed to scrape book details from {url}: {e}")
                
        logger.info(f"Scraping completed. Successfully collected data for {len(books_data)} books.")
        return books_data
