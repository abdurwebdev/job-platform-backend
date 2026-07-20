from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class StandardJob(BaseModel):
  title : str
  url : str
  company_name : str
  company_logo : Optional[str] = None
  category : str
  tags : List[str] = []
  job_type : str
  publication_date : Optional[datetime] = None
  salary : str = "Undisclosed"
  candidate_required_location : str
  description : str
  source : str
  remote : bool = False
  location : Optional[str] = None
  external_id : Optional[str] = None