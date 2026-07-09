from app.scrapper.remotive.client import get_jobs_from_remotive
from app.scrapper.remotive.parser import parse_remotive_jobs

def scrape_remotive_jobs():
  raw_jobs = get_jobs_from_remotive()
  jobs = parse_remotive_jobs(raw_jobs)
  
  return jobs