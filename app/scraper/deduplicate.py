import re

from app.scraper.schemas import StandardJob


def _normalize(text: str) -> str:
    """
    Lowercase, strip punctuation/whitespace noise, drop common suffixes
    that vary between sources (Inc., LLC, remote tags) so that
    "Backend Engineer" and "Backend Engineer (Remote)" at "Acme Inc."
    and "Acme" collapse to the same key.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)  # drop parenthetical noise
    text = re.sub(r"\b(inc|llc|ltd|corp|co)\b\.?", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def _dedupe_key(job: StandardJob) -> tuple[str, str, str]:
    return (
        _normalize(job.company_name),
        _normalize(job.title),
        _normalize(job.location or job.candidate_required_location or ""),
    )
    

def deduplicate_jobs(jobs: list[StandardJob]) -> list[StandardJob]:
    """
    Two-stage de-duplication:

    1. Exact URL match — the same posting scraped twice (or the same
       aggregator returning a job we already have).
    2. Normalized (company, title) match — the SAME job posted on
       multiple sources with different URLs (e.g. a company posts on
       both its own Greenhouse board and Remotive). This is the case
       the roadmap explicitly calls out: "the same job on 5 sites
       becomes one clean record."

    Keeps the first occurrence encountered for each key.
    """
    unique_jobs: list[StandardJob] = []
    seen_urls: set[str] = set()
    seen_keys: set[tuple[str, str]] = set()

    url_duplicates = 0
    cross_source_duplicates = 0

    for job in jobs:
        if job.url in seen_urls:
            url_duplicates += 1
            continue

        key = _dedupe_key(job)
        if key in seen_keys and key != ("", "",""):
            cross_source_duplicates += 1
            continue

        seen_urls.add(job.url)
        seen_keys.add(key)
        unique_jobs.append(job)

    if url_duplicates or cross_source_duplicates:
        from app.core.logger import logger

        logger.info(
            "Deduplication: "
            f"input={len(jobs)} "
            f"url_dupes={url_duplicates} "
            f"cross_source_dupes={cross_source_duplicates} "
            f"unique={len(unique_jobs)}"
        )

    return unique_jobs