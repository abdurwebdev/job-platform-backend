from typing import Any, List

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob
from app.scraper.utils import (
    format_salary_range,
    parse_timestamp,
    normalize_company_name,
)


class HimalayasScraper(BaseApiScraper):
    data_key = "jobs"

    def __init__(self):
        super().__init__(
            url="https://himalayas.app/jobs/api",
            source_name="Himalayas",
        )
    def parse(self, data: Any) -> List[StandardJob]:

        jobs: List[StandardJob] = []

        for item in data:

            description = self.clean_html(
                item.get("description", "")
            )

            salary = format_salary_range(
                min_val=item.get("minSalary"),
                max_val=item.get("maxSalary"),
                currency=item.get("currency"),
                period=item.get("salaryPeriod", "annual"),
            )

            categories = item.get("categories", [])
            category = (
                categories[0]
                if categories
                else "General"
            )

            location = (
                ", ".join(
                    item.get("locationRestrictions", [])
                )
                or "Remote"
            )

            publication_date = parse_timestamp(
                item.get("pubDate")
            )

            company_name = normalize_company_name(
                item.get("companyName"),
                item.get("companySlug"),
            )

            jobs.append(
                build_job(
                    title=item.get("title"),
                    url=item.get("applicationLink"),
                    company_name=company_name,
                    company_logo=item.get("companyLogo"),
                    category=category,
                    tags=categories,
                    job_type=item.get("employmentType") or "Full-time",
                    remote=True,
                    location=location,
                    publication_date=publication_date,
                    salary=salary,
                    candidate_required_location=location,
                    description=description,
                    source=self.source_name,
                    external_id=item.get("guid"),
                )
            )

        return jobs