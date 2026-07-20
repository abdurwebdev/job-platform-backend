"""
Run this the night before your demo:

    python -m app.scraper.verify_sources

It pings every configured Greenhouse/Lever company and tells you which
ones are dead (company migrated ATS, disabled their public board, etc.)
so you can delete those lines from registry.py before presenting.

Not part of the app's runtime — this is a one-off maintenance tool.
"""

import httpx

from app.scraper.registry import GREENHOUSE_COMPANIES, LEVER_COMPANIES


def check(url: str) -> tuple[bool, str]:
    try:
        r = httpx.get(url, timeout=10)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        data = r.json()
        jobs = data.get("jobs", data) if isinstance(data, dict) else data
        count = len(jobs) if isinstance(jobs, list) else 0
        if count == 0:
            return False, "0 jobs returned"
        return True, f"{count} jobs"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main():
    print("=== Greenhouse ===")
    dead_gh = []
    for token, name in GREENHOUSE_COMPANIES:
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
        ok, detail = check(url)
        print(f"{'OK  ' if ok else 'DEAD'} {name:20s} ({token}): {detail}")
        if not ok:
            dead_gh.append(token)

    print("\n=== Lever ===")
    dead_lever = []
    for slug, name in LEVER_COMPANIES:
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
        ok, detail = check(url)
        print(f"{'OK  ' if ok else 'DEAD'} {name:20s} ({slug}): {detail}")
        if not ok:
            dead_lever.append(slug)

    print("\n=== Summary ===")
    print(f"Dead Greenhouse tokens to remove: {dead_gh or 'none'}")
    print(f"Dead Lever slugs to remove: {dead_lever or 'none'}")


if __name__ == "__main__":
    main()
