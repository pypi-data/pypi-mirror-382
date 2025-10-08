from typing import Type
from .core import Target, Scraper


class ScraperFactory:
    """A simple registry pattern for scrapers."""

    _registry: dict[str, Type[Scraper]] = {}

    @classmethod
    def register(cls, name: str, scraper: Type[Scraper]) -> None:
        cls._registry[name] = scraper

    @classmethod
    def create(cls, target: Target) -> Scraper:
        scraper_cls = cls._registry.get(target.name)
        if not scraper_cls:
            raise ValueError(f"No scraper registered for: {target.name}")
        return scraper_cls(target)
