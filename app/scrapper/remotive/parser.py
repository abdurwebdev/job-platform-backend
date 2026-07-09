from bs4 import BeautifulSoup
from app.scrapper.schemas import StandardJob


def parse_remotive_jobs(jobs_from_remotive):
    data = jobs_from_remotive
    jobs = data.get('jobs', [])
    alljobsfromremotives = []
    
    for job in jobs:
        html_description = job.get("description", "")
        
        if not html_description:
            continue
            
        soup = BeautifulSoup(html_description, "html.parser")
        
        clean_description = soup.get_text(separator="\n", strip=True)
        
        standard_job = StandardJob(
            title=job.get("title"),
            company_name=job.get("company_name"),
            url=job.get("url"),
            category=job.get("category"),
            tags=job.get("tags"),
            job_type=job.get("job_type"),
            company_logo=job.get("company_logo"),
            publication_date=job.get("publication_date"),
            candidate_required_location=job.get("candidate_required_location"),
            salary=job.get("salary"),
            description=clean_description, 
            source="Remotive"
        )
        alljobsfromremotives.append(standard_job)
  
    return alljobsfromremotives