from typing import Any, Optional

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob
from app.scraper.utils import parse_timestamp


class LeverScraper(BaseApiScraper):
    """
    Generic Lever postings scraper. Reused per-company via company_slug.
    """

    data_key = None  # Lever returns a raw JSON array

    def __init__(self, company_slug: str, company_name: Optional[str] = None):
        self.company_name = company_name or company_slug.replace("-", " ").title()

        super().__init__(
            url=f"https://api.lever.co/v0/postings/{company_slug}?mode=json",
            source_name=f"Lever: {self.company_name}",
        )

    def map_item(
        self,
        item: Any,
    ) -> Optional[StandardJob]:

        categories = item.get("categories") or {}
        location = categories.get("location") or "Remote"

        description = self.clean_html(item.get("description", "") or "")

        created_at_ms = item.get("createdAt")
        publication_date = (
            parse_timestamp(created_at_ms / 1000) if created_at_ms else None
        )

        tags = [t for t in [categories.get("team"), categories.get("department")] if t]

        return build_job(
            title=item.get("text"),
            url=item.get("hostedUrl") or item.get("applyUrl"),
            company_name=self.company_name,
            category=categories.get("team") or "General",
            tags=tags,
            job_type=categories.get("commitment") or "Full-time",
            remote=(item.get("workplaceType") == "remote"),
            location=location,
            publication_date=publication_date,
            candidate_required_location=location,
            description=description,
            source=self.source_name,
            external_id=item.get("id"),
        )