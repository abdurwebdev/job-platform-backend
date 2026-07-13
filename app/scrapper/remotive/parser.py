import html
import nh3
from app.scrapper.schemas import StandardJob


def parse_remotive_jobs(jobs_from_remotive):
    data = jobs_from_remotive
    jobs = data.get('jobs', [])
    alljobsfromremotives = []
    
    ALLOWED_TAGS = {
        'p', 'b', 'i', 'strong', 'em', 'u', 'br',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'blockquote', 'pre', 'code', 'a'
    }
    
    # Keep href and target, and manually handle rel since link_rel=None is active now
    ALLOWED_ATTRIBUTES = {
        'a': {'href', 'target', 'rel'}
    }
    
    for job in jobs:
        html_description = job.get("description", "")
        
        if not html_description:
            continue
            
        html_description = html.unescape(html_description)
        
        try:
            # Added link_rel=None here to resolve the constraint exception
            clean_description = nh3.clean(
                html_description,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                link_rel=None
            )
        except Exception as e:
            print(f"nh3 cleaner error encountered: {e}")
            clean_description = html_description 

        if not clean_description.strip():
            clean_description = html_description
        print(clean_description)
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