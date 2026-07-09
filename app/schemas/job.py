from pydantic import BaseModel,ConfigDict
from typing import Optional,List

class JobUIOverviewSchema(BaseModel):
  model_config = ConfigDict(from_attributes = True)
  id:int
  title:str
  url:str
  company_name:str
  company_logo:Optional[str] = None
  category:str
  tags:List[str]
  job_type:str
  publication_date:str
  salary:str
  candidate_required_location:str
  source:str
  
class JobDetailOverview(JobUIOverviewSchema):
  description:Optional[str] = None