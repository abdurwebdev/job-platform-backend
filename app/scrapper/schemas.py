from dataclasses import dataclass
from typing import Optional

@dataclass
class StandardJob:
  title:str
  url:str
  company_name:str
  company_logo:Optional[str]
  category:str
  tags:list[str]
  job_type:str
  publication_date:str
  salary:str
  candidate_required_location:str
  description:str
  source:str