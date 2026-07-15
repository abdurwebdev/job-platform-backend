from app.scraper.schemas import StandardJob

def deduplicate_jobs(jobs:list[StandardJob]) -> list[StandardJob]:
  unique_jobs = []
  seen_urls = set()
  
  for job in jobs:
    if job.url in seen_urls:
      continue
    seen_urls.add(job.url)
    unique_jobs.append(job)
  
  return unique_jobs;