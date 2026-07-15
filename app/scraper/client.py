import requests
from requests.exceptions import ConnectTimeout, ReadTimeout, RequestException
from app.core.logger import logger
from typing import Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DEFAULT_TIMEOUT = (3.05, 10)


def get_json(url: str) -> Any:

    try:
        response = requests.get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)

        response.raise_for_status()

        data = response.json()

        return data
    except ConnectTimeout:
        logger.error(f"Connection timeout while requesting {url}")
        return None

    except ReadTimeout:
        logger.error(f"Connection timeout while requesting {url}")
        return None
    except RequestException as e:
        logger.exception(f"Failed to fetch {url}: {e}")
        return None
