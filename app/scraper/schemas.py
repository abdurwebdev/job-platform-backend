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
  
  



# from dataclasses import dataclass
# from typing import Optional

# @dataclass
# class StandardJob:
#   title:str
#   url:str
#   company_name:str
#   company_logo:Optional[str]
#   category:str
#   tags:list[str]
#   job_type:str
#   publication_date:str
#   salary:str
#   candidate_required_location:str
#   description:str
#   source:str