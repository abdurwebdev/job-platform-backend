from typing import Any, Optional

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob
from app.scraper.utils import parse_datetime


class GreenhouseScraper(BaseApiScraper):
    """
    Generic Greenhouse Job Board scraper. One class, reused for every
    company that hosts its careers page on Greenhouse — add a new source
    by adding a board_token to the config list, not by writing new code.

    Public, unauthenticated endpoint:
    https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
    """

    data_key = "jobs"

    def __init__(self, board_token: str, company_name: Optional[str] = None):
        self.company_name = company_name or board_token.replace("-", " ").title()

        super().__init__(
            url=(
                f"https://boards-api.greenhouse.io/v1/boards/"
                f"{board_token}/jobs?content=true"
            ),
            source_name=f"Greenhouse:{board_token}",
        )

    def map_item(
        self,
        item: Any,
    ) -> Optional[StandardJob]:

        location = (item.get("location") or {}).get("name") or "Remote"

        description = self.clean_html(item.get("content", "") or "")

        department = None
        for meta in item.get("metadata") or []:
            if meta.get("name") in ("Department", "Team"):
                value = meta.get("value")
                department = value if isinstance(value, str) else None
                break

        publication_date = (
            parse_datetime(item.get("updated_at")) if item.get("updated_at") else None
        )

        return build_job(
            title=item.get("title"),
            url=item.get("absolute_url"),
            company_name=self.company_name,
            category=department or "General",
            tags=[department] if department else [],
            job_type="Full-time",
            remote="remote" in location.lower(),
            location=location,
            publication_date=publication_date,
            candidate_required_location=location,
            description=description,
            source=self.source_name,
            external_id=str(item.get("id")) if item.get("id") else None,
        )
