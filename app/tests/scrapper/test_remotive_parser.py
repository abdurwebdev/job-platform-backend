import pytest
from app.scrapper.remotive.parser import parse_remotive_jobs


def test_single_scrapped():
  job = {
    "jobs":[
      {
        "title":"Backend Developer",
        "url":"https://url.com",
        "company_name":"Codeaza Technologies",
        "company_logo":"https://ogo.com",
        "category":"Coding",
        "tags":"['Rest']",
        "job_type":"freelance",
        "salary":"300000",
        "candidate_required_location":"Worldwide",
        "source":"Remotive",
        "description":"<h1>Hello</h1>"
      }
    ]
  }
  
  jobs = parse_remotive_jobs(job)
  
  assert len(jobs) == 1
  
  standard = jobs[0]
  
  assert standard.title == "Backend Developer"
  assert standard.url == "https://url.com"
  assert standard.company_name == "Codeaza Technologies"
  assert standard.company_logo == "https://ogo.com"
  assert standard.category == "Coding"
  assert standard.tags == "['Rest']"
  assert standard.job_type == "freelance"
  assert standard.salary == "300000"
  assert standard.candidate_required_location == "Worldwide"
  assert standard.source == "Remotive"
  assert standard.description == "Hello"
  
def test_empty_jobs():
  data = {"jobs":[]}
  result = parse_remotive_jobs(data)
  
  assert result == []
  
def test_missing_jobs_key():
  data = {}
  jobs = parse_remotive_jobs(data)
  assert jobs == []
  
def test_skip_job_without_description():
  job = {
    "jobs":[
      {
        "title":"Backend Developer",
        "url":"https://url.com",
        "company_name":"Codeaza Technologies",
        "company_logo":"https://ogo.com",
        "category":"Coding",
        "tags":"['Rest']",
        "job_type":"freelance",
        "salary":"300000",
        "candidate_required_location":"Worldwide",
        "source":"Remotive",
        "description":""
      }
    ]
  }
  jobs = parse_remotive_jobs(job)
  assert jobs == []
  
def test_html_is_clean():
  job = {
    "jobs":[
      {
        "title":"Backend Developer",
        "url":"https://url.com",
        "company_name":"Codeaza Technologies",
        "company_logo":"https://ogo.com",
        "category":"Coding",
        "tags":"['Rest']",
        "job_type":"freelance",
        "salary":"300000",
        "candidate_required_location":"Worldwide",
        "source":"Remotive",
        "description":"""
                    <h1>Requirements</h1>
                    <ul>
                        <li>Python</li>
                        <li>FastAPI</li>
                    </ul>
                """
      }
    ]
  }
  
  jobs = parse_remotive_jobs(job)
  assert jobs[0].description.strip() == "Requirements\nPython\nFastAPI"
  

def test_multiple_jobs():
  job = {
    "jobs":[
      {
        "title":"Backend Developer",
        "url":"https://url.com",
        "company_name":"Codeaza Technologies",
        "company_logo":"https://ogo.com",
        "category":"Coding",
        "tags":"['Rest']",
        "job_type":"freelance",
        "salary":"300000",
        "candidate_required_location":"Worldwide",
        "source":"Remotive",
        "description":"<h1>Hello</h1>"
      },
      {
        "title":"AI Engineer",
        "url":"https://url.com",
        "company_name":"Open AI",
        "company_logo":"https://ogo.com",
        "category":"Coding",
        "tags":"['Rest']",
        "job_type":"freelance",
        "salary":"300000",
        "candidate_required_location":"Worldwide",
        "source":"Remotive",
        "description":"<h1>Hello</h1>"
      }
    ]
  }
  jobs = parse_remotive_jobs(job)
  
  assert jobs[0].title == "Backend Developer"
  assert jobs[1].title == "AI Engineer"