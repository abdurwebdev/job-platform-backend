import html
import bleach
from app.scrapper.schemas import StandardJob


def parse_remotive_jobs(jobs_from_remotive):
    data = jobs_from_remotive
    jobs = data.get('jobs', [])
    alljobsfromremotives = []
    
    # 1. Elements allowed to pass through the filter
    ALLOWED_TAGS = [
        'p', 'b', 'i', 'strong', 'em', 'u', 'br',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'blockquote', 'pre', 'code', 'a'
    ]
    
    # 2. Map structural elements to allowed attributes
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'target', 'rel']
    }
    
    for job in jobs:
        html_description = job.get("description", "")
        
        if not html_description:
            continue
            
        # Standardize HTML markup symbols safely
        html_description = html.unescape(html_description)
        
        try:
            # 3. Clean string via pure-Python bleach engine
            clean_description = bleach.clean(
                html_description,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True  # Strips out unauthorized structural markers cleanly
            )
        except Exception as e:
            print(f"Bleach cleaner error encountered: {e}")
            clean_description = html_description 

        if not clean_description.strip():
            clean_description = html_description
        
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