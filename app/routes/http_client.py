import time

import httpx

from app.core.logger import logger
from app.core.rate_limiter import host_rate_limiter


class HTTPClient:
    def __init__(
        self,
        retries: int = 3,
        timeout: int = 20,
        backoff_factor: int = 2,
    ):
        self.retries = retries
        self.timeout = timeout
        self.backoff_factor = backoff_factor

    def get(
        self,
        url: str,
        *,
        scraper_name: str = "Unknown",
        **kwargs,
    ) -> httpx.Response:

        delay = 1

        for attempt in range(1, self.retries + 1):

            logger.info(
                f"[{scraper_name}] Attempt {attempt} -> {url}"
            )

            # Config-driven sources (e.g. 21 Greenhouse companies) all
            # hit the same host — space out requests per-host so we
            # don't get 429'd before retries even get a chance to help.
            host_rate_limiter.wait_for_turn(url)

            try:

                response = httpx.get(
                    url,
                    timeout=self.timeout,
                    **kwargs,
                )

                if response.status_code in [429, 500, 502, 503, 504]:

                    logger.warning(
                        f"[{scraper_name}] "
                        f"HTTP {response.status_code}"
                    )

                    raise httpx.HTTPStatusError(
                        "Retry",
                        request=response.request,
                        response=response,
                    )

                logger.info(
                    f"[{scraper_name}] Success"
                )

                return response

            except (
                httpx.TimeoutException,
                httpx.ConnectError,
                httpx.HTTPStatusError,
            ) as e:

                logger.warning(
                    f"[{scraper_name}] "
                    f"Attempt {attempt} failed "
                    f"({type(e).__name__})"
                )

                if attempt == self.retries:
                    logger.error(
                        f"[{scraper_name}] "
                        "Maximum retries exceeded."
                    )
                    raise

                logger.info(
                    f"[{scraper_name}] "
                    f"Retrying in {delay}s..."
                )

                time.sleep(delay)

                delay *= self.backoff_factor


http_client = HTTPClient()