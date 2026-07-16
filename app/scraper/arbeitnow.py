from typing import Any, Optional

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob


class ArbeitnowScraper(BaseApiScraper):
    data_key = "data"

    def __init__(self):
        super().__init__(
            url="https://www.arbeitnow.com/api/job-board-api",
            source_name="Arbeitnow",
        )

    def map_item(
        self,
        item: Any,
    ) -> Optional[StandardJob]:
        description = self.clean_html(
            item.get("description", "")
        )

        return build_job(
            title=item.get("title"),
            url=item.get("url"),
            company_name=item.get("company_name"),
            company_logo=item.get("company_logo"),
            category=item.get("category") or "General",
            tags=item.get("tags", []),
            job_type=item.get("job_type") or "Full-time",
            publication_date=item.get("publication_date"),
            salary=item.get(
                "salary",
                "Undisclosed",
            ),
            candidate_required_location=(
                item.get(
                    "candidate_required_location"
                )
                or "Global"
            ),
            description=description,
            source=self.source_name,
            remote=item.get("remote"),
            location=item.get("location"),
            external_id=item.get("slug"),
        )