from abc import abstractmethod
from typing import Any, List, Optional

from app.scraper.base import BaseScraper
from app.scraper.client import get_json
from app.scraper.schemas import StandardJob


class BaseApiScraper(BaseScraper):
    data_key: Optional[str] = None

    def __init__(self, url: str, source_name: str):
        self.url = url
        self.source_name = source_name

    def scrape(self) -> List[StandardJob]:
        response = get_json(
            self.url,
            scraper_name=self.source_name,
        )

        if response is None:
            return []

        data = response

        if self.data_key:
            data = response.get(self.data_key, [])

        return self.parse(data)

    def parse(self, data: Any) -> List[StandardJob]:
        jobs: List[StandardJob] = []

        for item in data:
            job = self.map_item(item)

            if job is not None:
                jobs.append(job)

        return jobs

    @abstractmethod
    def map_item(self, item: Any) -> Optional[StandardJob]:
        pass
