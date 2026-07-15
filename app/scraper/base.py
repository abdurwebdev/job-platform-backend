from abc import ABC, abstractmethod
from typing import Any, List

from app.scraper.schemas import StandardJob
from app.scraper.utils import clean_html


class BaseScraper(ABC):
    """
    Base contract for every scraper.

    Every scraper must:

    • provide a source_name
    • provide a url
    • implement scrape()
    • implement parse()

    Everything else is shared here.
    """

    source_name: str
    url: str

    def clean_html(self, html_content: str) -> str:
        """
        Shared HTML cleaner.
        """
        return clean_html(html_content)

    @abstractmethod
    def scrape(self) -> List[StandardJob]:
        """
        Download data from API.
        """
        pass

    @abstractmethod
    def parse(self, data: Any) -> List[StandardJob]:
        """
        Convert raw API response into StandardJob objects.
        """
        pass