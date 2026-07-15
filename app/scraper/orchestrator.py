import time
from app.core.logger import logger
from app.scraper.registry import SCRAPERS
from app.scraper.result import  ScrapeResult
from app.scraper.schemas import StandardJob
from app.scraper.deduplicate import deduplicate_jobs
from typing import List

def run_all_scrapers() -> List[ScrapeResult]:
    all_scrape_results: List[ScrapeResult] = []
    
    for scraper_class in SCRAPERS:
        scraper = scraper_class()
        start_time = time.perf_counter()
        
        try:
            logger.info(f"--- Running {scraper.source_name} ---")
            jobs = scraper.scrape()
            
            # Calculate duration
            duration = int((time.perf_counter() - start_time) * 1000)
            
            # Store success result
            all_scrape_results.append(ScrapeResult(
                source=scraper.source_name,
                jobs=jobs,
                count=len(jobs),
                success=True,
                duration_ms=duration
            ))
            logger.info(f"Collected {len(jobs)} jobs from {scraper.source_name}")

        except Exception as e:
            duration = int((time.perf_counter() - start_time) * 1000)
            logger.exception(f"{scraper.source_name} failed.")
            
            # Store failure result
            all_scrape_results.append(ScrapeResult(
                source=scraper.source_name,
                jobs=[],
                count=0,
                success=False,
                error=str(e),
                duration_ms=duration
            ))

    # Optional: Log summary of failures
    failed = [r.source for r in all_scrape_results if not r.success]
    if failed:
        logger.warning(f"Failed scrapers: {', '.join(failed)}")

    return all_scrape_results