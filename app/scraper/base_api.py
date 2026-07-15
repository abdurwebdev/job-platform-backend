from abc import ABC
from typing import List

from app.scraper.base import BaseScraper
from app.scraper.client import get_json
from app.scraper.schemas import StandardJob


class BaseApiScraper(BaseScraper, ABC):
    """
    Base class for API-based scrapers.

    Child classes only need to define:
    - source_name
    - url
    - data_key (optional)
    - parse()
    """

    data_key: str | None = None

    def __init__(self, url: str, source_name: str):
        self.url = url
        self.source_name = source_name

    def scrape(self) -> List[StandardJob]:
        data = get_json(self.url)

        if not data:
            return []

        if self.data_key:
            data = data.get(self.data_key, [])

        return self.parse(data)