from app.database.database import Base
from sqlalchemy import Column,Integer,String,ARRAY,Text

class Job(Base):
  __tablename__ = "jobs"
  id = Column(Integer,primary_key = True,index = True)
  title = Column(String)
  url = Column(String,unique = True,nullable = False)
  company_name = Column(String)
  company_logo = Column(String)
  category = Column(String)
  tags = Column(ARRAY(String))
  job_type = Column(String)
  publication_date = Column(String)
  salary = Column(String)
  candidate_required_location = Column(String)
  description = Column(Text,nullable = True)
  source = Column(String)

  