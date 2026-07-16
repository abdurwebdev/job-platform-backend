import html
from typing import Any, Optional

from app.scraper.base_api import BaseApiScraper
from app.scraper.job_factory import build_job
from app.scraper.schemas import StandardJob
from app.scraper.utils import (
    clean_jobicy_boilerplate,
    format_salary_range,
    parse_datetime,
)


class JobicyScraper(BaseApiScraper):
    data_key = "jobs"

    def __init__(self):
        super().__init__(
            url="https://jobicy.com/api/v2/remote-jobs",
            source_name="Jobicy",
        )

    def map_item(
        self,
        item: Any,
    ) -> Optional[StandardJob]:

        description = self.clean_html(
            item.get("jobDescription", "")
        )

        description = clean_jobicy_boilerplate(
            description
        )

        industries = [
            html.unescape(ind)
            for ind in item.get("jobIndustry", [])
        ]

        category = (
            industries[0]
            if industries
            else "General"
        )

        publication_date = parse_datetime(
            item.get("pubDate")
        )

        salary = format_salary_range(
            min_val=item.get("salaryMin"),
            max_val=item.get("salaryMax"),
            currency=item.get(
                "salaryCurrency",
                "USD",
            ),
            period=item.get(
                "salaryPeriod",
                "yearly",
            ),
        )

        return build_job(
            title=html.unescape(
                item.get("jobTitle", "")
            ),
            url=item.get("url"),
            company_name=html.unescape(
                item.get(
                    "companyName",
                    "Remote Company",
                )
            ),
            company_logo=item.get("companyLogo"),
            category=category,
            tags=industries,
            job_type=item.get(
                "jobType",
                ["Full-Time"],
            )[0],
            remote=True,
            location=item.get(
                "jobGeo",
                "Remote",
            ),
            publication_date=publication_date,
            salary=salary,
            candidate_required_location=item.get(
                "jobGeo",
                "Global",
            ),
            description=description,
            source=self.source_name,
            external_id=str(item.get("id")),
        )