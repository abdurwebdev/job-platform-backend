import time
from urllib.parse import urlparse


class HostRateLimiter:
    """
    Enforces a minimum delay between requests to the same host.

    Scrapers run sequentially, one at a time, so this doesn't need
    threading/async coordination — it just remembers the last time we
    hit each host and sleeps if we're about to hit it again too soon.

    This matters once you're config-driven: 25 "different sources" can
    all be boards-api.greenhouse.io, and that host will start returning
    429s if you hit it 25 times back-to-back with no gap.
    """

    def __init__(self, min_interval_seconds: float = 0.5):
        self.min_interval = min_interval_seconds
        self._last_call_at: dict[str, float] = {}

    def wait_for_turn(self, url: str) -> None:
        host = urlparse(url).netloc
        last = self._last_call_at.get(host)
        now = time.monotonic()

        if last is not None:
            elapsed = now - last
            remaining = self.min_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

        self._last_call_at[host] = time.monotonic()


host_rate_limiter = HostRateLimiter()
