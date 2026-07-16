from calendar import timegm
from datetime import datetime, timezone
from typing import Any, List, Optional

import feedparser  # pip install feedparser

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob

RSS_URL = "https://weworkremotely.com/remote-jobs.rss"


class WeWorkRemotelyScraper(BaseApiScraper):
    def __init__(self):
        super().__init__(url=RSS_URL, source_name="WeWorkRemotely")

    def scrape(self) -> List[StandardJob]:
        feed = feedparser.parse(self.url)
        jobs = []
        for entry in feed.entries:
            job = self.map_item(entry)
            if job:
                jobs.append(job)
        return jobs

    @staticmethod
    def _parse_date(entry: Any) -> Optional[datetime]:
        parsed = entry.get("published_parsed")
        if not parsed:
            return None
        # struct_time from feedparser is already in UTC
        return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)

    def map_item(self, item: Any) -> Optional[StandardJob]:
        raw_title = item.get("title", "")
        if ":" in raw_title:
            company_name, title = raw_title.split(":", 1)
        else:
            company_name, title = None, raw_title

        description = self.clean_html(item.get("summary", ""))
        category = item["tags"][0]["term"] if item.get("tags") else None

        return build_job(
            title=title.strip(),
            url=item.get("link"),
            company_name=company_name.strip() if company_name else "Not specified",
            company_logo=None,
            category=category or "Not specified",
            tags=[],
            job_type="Not specified",
            publication_date=self._parse_date(item),
            salary="Undisclosed",
            candidate_required_location="Not specified",
            description=description,
            source=self.source_name,
        )