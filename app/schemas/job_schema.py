from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime # Import datetime

class JobUIOverviewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    url: str
    company_name: str
    company_logo: Optional[str] = None
    category: str
    tags: List[str]
    job_type: str
    # Change this from str to datetime
    publication_date: Optional[datetime] = None 
    salary: str
    candidate_required_location: str
    source: str
 
class JobDetailOverview(JobUIOverviewSchema):
    description: Optional[str] = None
    
# schemas/job_schema.py — add this
class PaginatedJobsResponse(BaseModel):
    jobs: List[JobUIOverviewSchema]
    total: int
    page: int
    limit: int