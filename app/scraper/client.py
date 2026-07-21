from app.core.http_client import http_client
import httpx
from app.core.logger import logger
from typing import Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}



def get_json(url: str,scraper_name:str):

    try:
        response = http_client.get(
            url,
            headers=HEADERS,
            scraper_name=scraper_name
        )

        response.raise_for_status()

        return response.json()

    except httpx.HTTPError as e:
        logger.exception(f"Failed to fetch {url}: {e}")
        return None