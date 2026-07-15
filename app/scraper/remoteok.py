from typing import Any, List

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob
from app.scraper.utils import (
    clean_remoteok_boilerplate,
    format_salary_range,
    normalize_location,
    parse_datetime,
)


class RemoteOkScraper(BaseApiScraper):
    data_key = None

    def __init__(self):
        super().__init__(
            url="https://remoteok.com/api",
            source_name="Remote OK",
        )
        
    def parse(self, data: Any) -> List[StandardJob]:
        jobs: List[StandardJob] = []

        for item in data:
            # Skip API metadata object
            if "legal" in item or "id" not in item:
                continue

            description = self.clean_html(
                item.get("description", "")
            )
            description = clean_remoteok_boilerplate(
                description
            )

            tags = item.get("tags", [])
            category = (
                tags[0].title()
                if tags
                else "General"
            )

            salary = format_salary_range(
                item.get("salary_min"),
                item.get("salary_max"),
                currency="USD",
                period="annual",
            )

            location = normalize_location(
                item.get("location")
            )

            jobs.append(
                build_job(
                    title=item.get("position", ""),
                    url=item.get("apply_url")
                    or item.get("url"),
                    company_name=item.get(
                        "company",
                        "Remote Company",
                    ),
                    company_logo=item.get("logo"),
                    category=category,
                    tags=tags,
                    job_type="Full-time",
                    remote=True,
                    location=location,
                    publication_date=parse_datetime(
                        item.get("date")
                    ),
                    salary=salary,
                    candidate_required_location=location,
                    description=description,
                    source=self.source_name,
                    external_id=str(item.get("id")),
                )
            )

        return jobs