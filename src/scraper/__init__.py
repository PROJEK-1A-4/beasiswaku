"""
Scraper module - Web scraping and data collection
Owner: KEMAL

Main Functions:
- scrape_beasiswa_data(): Main scraping function for all categories
- scrape_category(): Scrape specific category with pagination
- get_scraper_thread(): Get ScraperThread for background scraping
- save_backup(): Save scraped data to JSON backup
"""

from .scraper import (
    scrape_beasiswa_data,
    scrape_category,
    extract_beasiswa_info,
    get_scraper_thread,
    save_backup,
)

# ScraperThread only available if PyQt6 is installed
try:
    from .scraper import ScraperThread
except ImportError:
    ScraperThread = None

__all__ = [
    'scrape_beasiswa_data',
    'scrape_category',
    'extract_beasiswa_info',
    'get_scraper_thread',
    'save_backup',
]
