from fastapi import APIRouter,Depends,Response
from sqlalchemy.orm import Session
from app.services.job_service import get_all_jobs,get_job_details,save_jobs_to_db
from app.database.database import get_db
from app.scraper.orchestrator import run_all_scrapers

from app.schemas.job_schema import JobUIOverviewSchema,JobDetailOverview

router = APIRouter(
  prefix = "/api/job",
  tags = ["Jobs"]
)
@router.post("/scrape")
def scrape_jobs(db: Session = Depends(get_db)):
    
    scrape_reports = run_all_scrapers()
    
   
    all_jobs = []
    for report in scrape_reports:
        all_jobs.extend(report.jobs)
    
   
    save_jobs_to_db(all_jobs, db)
    
    return scrape_reports

@router.get("/all",response_model = list[JobUIOverviewSchema])
def getall(response: Response,db:Session = Depends(get_db)):
  response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
  response.headers["Pragma"] = "no-cache"
  return get_all_jobs(db) 

@router.get("/job-detail/{jobId}",response_model = JobDetailOverview)
def getdetails(jobId:int,db:Session = Depends(get_db)):
  return get_job_details(jobId,db)