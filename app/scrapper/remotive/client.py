import requests
from requests.exceptions import RequestException, Timeout
from app.core.logger import logger

def get_jobs_from_remotive() -> dict:
    url = "https://remotive.com/api/remote-jobs"
    try:
        response = requests.get(url, timeout=(3.05, 10))
        response.raise_for_status()
        return response.json()
        
    except Timeout as e:
        logger.error(f"Timeout occurred fetching jobs from Remotive: {e}")
        return {}
        
    except RequestException as e:
        logger.error(f"Unexpected network error fetching jobs from Remotive: {e}")
        return {}