from sqlalchemy import Column, Integer, String, ARRAY, Text, DateTime
from app.database.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(300), nullable=False)                    # Increased
    url = Column(String(500), unique=True, index=True, nullable=False)  # URLs can be long
    company_name = Column(String(200), nullable=False)             # Increased
    company_logo = Column(String(500))                             # Logo URLs
    category = Column(String(150))                                 # Increased
    tags = Column(ARRAY(String))                                   # Already good
    job_type = Column(String(100))                                 # e.g. Full Time, Contract
    publication_date = Column(DateTime(timezone=True), nullable=True)
    salary = Column(String(100))                                   # e.g. "$100k - $150k"
    candidate_required_location = Column(String(500))              # ← This was the main problem
    description = Column(Text, nullable=True)                      # Already good (unlimited)
    source = Column(String(50))                                    # e.g. Himalayas, RemoteOK