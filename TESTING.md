# Backend — what's in this zip and how to test it

## Where each file goes

Everything here mirrors the real repo structure — copy each file to the
same relative path in `job-platform-backend/`, overwriting what's there.

```
job-platform-backend/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── README.md
├── .github/workflows/scrape.yml      (overwrite — cron disabled)
└── app/
    ├── main.py                        (overwrite)
    ├── config/config.py                (overwrite)
    ├── scraper/
    │   ├── orchestrator.py             (overwrite)
    │   └── scheduler.py                (NEW file)
    ├── routes/job_routes.py            (overwrite)
    └── tests/
        ├── conftest.py                 (NEW — and delete any confest.py
        │                                 typo'd file if one exists)
        └── test_job_routes.py          (overwrite, if already present)
```

## What changed and why

- **Scraping now runs inside the container**, not via GitHub Actions. A
  background thread (`app/scraper/scheduler.py`) starts on app startup,
  waits 60s, then scrapes every `SCRAPE_INTERVAL_HOURS` (default 6).
- **`orchestrator.py`** gained `run_and_save_jobs()` — the shared
  scrape→dedupe→save pipeline, used by both the manual `POST /scrape`
  route and the new scheduler, so there's one source of truth instead of
  two copies that could drift.
- **The GitHub Actions cron is disabled** (not deleted) — its `schedule:`
  trigger is commented out in `scrape.yml`, `workflow_dispatch` is kept
  for manual/emergency runs.
- **`conftest.py`** — if your repo had a typo'd `confest.py`, that's why
  route tests weren't picking up their test DB placeholder. Fixed here.

## How to test locally, step by step

### 1. Install and run the test suite (no Docker needed for this part)
```bash
pip install -r requirements.txt
python -m pytest app/tests/ -v
```
All tests should pass (17 as of this change). This alone confirms the
route refactor didn't break the filter/pagination contract.

### 2. Bring up the full stack with Docker
```bash
docker compose up --build
```
Watch the logs. You should see, in order:
- `Database connected and tables verified successfully.`
- `Scheduler started: scraping every 6.0h, first run in 60s.`

### 3. Confirm the scheduler actually fires on its own
This is the main thing to prove — **no curl command should be needed**.

If you don't want to wait 6 hours, override the interval for this test
run. Create a `.env` file (copy `.env.example`) and uncomment:
```
SCHEDULER_ENABLED=true
SCRAPE_INTERVAL_HOURS=0.05
```
That's ~3 minutes. Restart `docker compose up --build`, wait ~90 seconds
(the 60s startup delay + a bit), and watch the logs for:
```
Scheduler: starting scrape run.
...
Scheduled scrape complete: {...}
```
If you see that without ever running curl yourself, the in-container
scheduler is working. **Remove the `.env` overrides afterward** so it
goes back to the real 6-hour production interval.

### 4. Confirm nothing else broke
While the container's running:
```bash
curl "http://localhost:8000/api/job/all?category=Engineering&sort=salary&limit=5"
curl "http://localhost:8000/api/job/all?type=Full-time"
curl -X POST "http://localhost:8000/api/job/scrape?batch_index=0&batch_size=2"
curl "http://localhost:8000/api/health/scrapers"
```
All should behave exactly as before — filters working, manual trigger
still available, health data populated.

### 5. Confirm a clean rebuild persists data
```bash
docker compose down
docker compose up --build
```
Jobs scraped in step 3 should still be there — proves the Postgres volume
persists across rebuilds, not just within one running container.

## Before deploying to Coolify

- Remove any `SCHEDULER_ENABLED`/`SCRAPE_INTERVAL_HOURS` overrides from
  your local `.env` — production should use the real 6-hour default
- Set `SCRAPE_SECRET` to a real value if `POST /api/job/scrape` needs to
  stay protected in production
- Confirm with Usama whether Coolify provides its own Postgres or you're
  pointing at the existing Neon database — `DATABASE_URL` needs to match
  whichever one he says
