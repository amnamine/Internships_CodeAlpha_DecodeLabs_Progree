# Scraper module initialization
from .pipeline import ScraperPipeline
from .client import ScrapeClient
from .parser import BookParser

__all__ = ["ScraperPipeline", "ScrapeClient", "BookParser"]
