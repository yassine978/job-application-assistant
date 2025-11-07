"""Scrapers module for job data collection."""

from scrapers.base_scraper import BaseScraper
from scrapers.welcome_scraper import WelcomeToJungleScraper, welcome_scraper
from scrapers.adzuna_client import AdzunaClient, adzuna_client
from scrapers.scraper_factory import ScraperFactory, scraper_factory

__all__ = [
    'BaseScraper',
    'WelcomeToJungleScraper',
    'welcome_scraper',
    'AdzunaClient',
    'adzuna_client',
    'ScraperFactory',
    'scraper_factory'
]
