import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class Target:
    """A generic scrape target. Extend this with custom metadata as needed."""

    name: str
    start_url: str
    meta: Dict[str, Any] = field(default_factory=dict)


class Scraper(abc.ABC):
    """
    Base class for defining a scraper.
    Subclass this and implement the abstract methods below.
    """

    def __init__(self, target: Target):
        self.target = target
        self._discovered_urls: List[str] = []
        self._scraped_data: List[Dict[str, Any]] = []

    @abc.abstractmethod
    def is_valid_url(self, url: str) -> bool:
        """
        Determine whether the given URL is valid and should be scraped.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def discover_urls(self, page: Any, known: Set[str]) -> List[str]:
        """
        Return a list of new URLs to scrape next.
        Should deduplicate against `known` to avoid re-scraping.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def scrape_page(self, page: Any, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from a single URL.
        Return None to skip or ignore the page.
        """
        raise NotImplementedError

    async def fetch_round(self, known: Set[str]) -> List[Dict[str, Any]]:
        """
        Orchestrate a single round of scraping:
        - Discover new URLs
        - Validate and scrape each one
        Returns a list of structured results.
        """
        raise NotImplementedError

    def get_discovered_urls(self) -> List[str]:
        """Return all valid URLs discovered during scraping."""
        return [url for url in self._discovered_urls if self.is_valid_url(url)]

    def get_scraped_data(self) -> List[Dict[str, Any]]:
        """Return all structured data collected from scraped pages."""
        return self._scraped_data
