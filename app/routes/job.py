from fastapi import APIRouter,Depends,Response
from sqlalchemy.orm import Session
from app.services.job import get_alljobs,save_jobs_to_db,showdetails
from app.database.database import get_db
from app.scrapper.remotive.scraper import scrape_remotive_jobs
from app.schemas.job import JobUIOverviewSchema,JobDetailOverview

router = APIRouter(
  prefix = "/api/job",
  tags = ["Jobs"]
)

@router.post("/scrape")
def scrape_jobs(db:Session = Depends(get_db)):
  jobs = scrape_remotive_jobs()
  return save_jobs_to_db(jobs,db)

@router.get("/all",response_model = list[JobUIOverviewSchema])
def getall(response: Response,db:Session = Depends(get_db)):
  response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
  response.headers["Pragma"] = "no-cache"
  return get_alljobs(db) 

@router.get("/job-detail/{jobId}",response_model = JobDetailOverview)
def getdetails(jobId:int,db:Session = Depends(get_db)):
  return showdetails(jobId,db)