from typing import Any, List, Optional

import httpx

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob

ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
ALGOLIA_ITEM_URL = "https://hn.algolia.com/api/v1/items/{item_id}"


class HackerNewsHiringScraper(BaseApiScraper):
    """
    Scrapes the monthly 'Ask HN: Who is hiring?' thread via the free,
    keyless Algolia HN Search API (https://hn.algolia.com/api).

    Flow:
      1. Find the most recent 'Who is hiring' story (author: whoishiring).
      2. Fetch that story's full comment tree.
      3. Treat each top-level comment as one job posting.
    """

    def __init__(self):
        super().__init__(
            url=ALGOLIA_SEARCH_URL,
            source_name="HackerNews (Who is Hiring)",
        )

    def _find_latest_thread_id(self) -> Optional[str]:
        params = {
            "query": "Who is hiring",
            "tags": "story,author_whoishiring",
            "hitsPerPage": 1,
        }
        resp = httpx.get(self.url, params=params, timeout=15)
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        return hits[0]["objectID"] if hits else None

    def _fetch_top_level_comments(self) -> List[Any]:
        thread_id = self._find_latest_thread_id()
        if not thread_id:
            return []

        resp = httpx.get(ALGOLIA_ITEM_URL.format(item_id=thread_id), timeout=15)
        resp.raise_for_status()
        return resp.json().get("children", []) or []

    def scrape(self) -> List[StandardJob]:
        jobs = []
        for comment in self._fetch_top_level_comments():
            job = self.map_item(comment)
            if job:
                jobs.append(job)
        return jobs

    def map_item(self, item: Any) -> Optional[StandardJob]:
        text = item.get("text") or ""
        if not text or item.get("dead") or item.get("deleted"):
            return None

        description = self.clean_html(text)
        title_line = description.strip().split("\n")[0][:120] or "Who is Hiring listing"

        return build_job(
            title=title_line,
            url=f"https://news.ycombinator.com/item?id={item.get('id')}",
            company_name="Not specified",
            company_logo=None,
            category="Not specified",
            tags=[],
            job_type="Not specified",
            publication_date=item.get("created_at"),
            salary="Undisclosed",
            candidate_required_location="Not specified",
            description=description,
            source=self.source_name,
        )
            