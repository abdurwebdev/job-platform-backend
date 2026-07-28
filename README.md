# Rozgar Job Platform — Backend

FastAPI service that scrapes jobs from 50+ sources, de-duplicates them, and
serves them through a searchable/filterable API to
[rozgar.codeaza.org](https://rozgar.codeaza.org). Built as part of the
Codeaza Engineering Internship.

## Stack

- **FastAPI** + **SQLAlchemy** (sync) + **Postgres**
- **BeautifulSoup / httpx** for scraping (no headless browser — sources are
  plain HTML/JSON, no anti-bot JS challenges to beat yet)
- Deployed as serverless functions on **Vercel** (`vercel.json`); also
  runnable in **Docker** for local dev (see below)
- Scheduled scraping via a **GitHub Actions cron job** (`.github/workflows/scrape.yml`),
  not a server-side scheduler — see [Scheduling](#scheduling) for why

## Running locally with Docker (recommended)

```bash
docker compose up --build
```

This starts two containers:
- `db` — a disposable local Postgres 16, persisted in a named volume
  (`rozgar_pg_data`), completely separate from the Neon/prod database
- `backend` — the FastAPI app, bind-mounted with `--reload` so code edits
  apply without rebuilding

Then:
```bash
curl http://localhost:8000/                      # {"message": "Welcome to job portal"}
curl http://localhost:8000/api/job/all            # paginated jobs, empty on a fresh DB
curl -X POST http://localhost:8000/api/job/scrape # populate it — see note below first
```

Copy `.env.example` to `.env` if you want to set `SCRAPE_SECRET` locally;
`DATABASE_URL` is already wired to the `db` container in `docker-compose.yml`
and doesn't need setting.

To wipe the local DB and start clean: `docker compose down -v`.

⚠️ **Don't call `POST /api/job/scrape` with no params for a quick test** — it
runs all 50+ sources sequentially in one request and can take minutes. Use a
single batch instead, exactly like the GitHub Actions workflow does:
```bash
curl -X POST "http://localhost:8000/api/job/scrape?batch_index=0&batch_size=2"
```

## Running locally without Docker

```bash
python -m venv venv
venv\Scripts\activate        # or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
# create a .env with DATABASE_URL pointing at a real Postgres instance
uvicorn app.main:app --reload
```

## API reference

All routes are prefixed `/api`.

### `GET /job/all`
Paginated, searchable, filterable job listing.

| Query param | Notes |
|---|---|
| `page` | default `1` |
| `limit` | default `20` |
| `search` | matches job title (`ilike`) |
| `category` | exact match, case-insensitive |
| `type` | ⚠️ **query key is `type`, not `job_type`** — the route aliases it to match what the frontend (`JobsGridClient.tsx`) sends. If you're calling this API from somewhere new, send `type=`, not `job_type=` |
| `location` | substring match against `candidate_required_location` |
| `sort` | `newest` (default), `alphabetical`, or `salary` |

### `GET /job/job-detail/{jobId}`
Full detail for a single job, 404 if not found.

### `GET /job/scrape/meta?batch_size=6`
Returns `total_sources` / `total_batches` for a given batch size. Used by
the GitHub Actions workflow to know how many batches to loop through.

### `POST /job/scrape`
Runs scrapers and saves results. Omit `batch_index`/`batch_size` to run
everything in one call (slow — see warning above), or pass both to run one
batch. If `SCRAPE_SECRET` is set, requires an `X-Scrape-Secret` header
matching it.

### `GET /health/scrapers`
Per-source health: last run time, success/failure, consecutive failure
count. Check this after any scrape run — with 50+ live sources, some will
legitimately go down or change their page structure over time.

## Scheduling

Scraping runs automatically from **inside the running container** — a
background thread (`app/scraper/scheduler.py`) started in `main.py`'s
lifespan hook. On startup it waits 60s, then runs the full scrape-and-save
pipeline (`run_and_save_jobs()` in `orchestrator.py`) every
`SCRAPE_INTERVAL_HOURS` (default 6). No external trigger required — this
is why the app needs to run as a long-lived container rather than
serverless functions.

`SCHEDULER_ENABLED` and `SCRAPE_INTERVAL_HOURS` are both env vars (see
`.env.example`) — useful to override locally (e.g. a short interval) while
testing, without touching code.

The old GitHub Actions cron (`.github/workflows/scrape.yml`) that used to
trigger scraping externally is **disabled** as of the move to in-container
scheduling — its `schedule:` trigger is commented out, but the file is
kept with `workflow_dispatch` only, in case a manual full-batch run from
CI is ever useful (e.g. backfilling after an outage) without touching the
live container.

## Scraper sources

Two shapes, both registered in `app/scraper/registry.py`:

- **`DIRECT_SCRAPERS`** — one bespoke class per site (RemoteOK, Remotive,
  Himalayas, Jobicy, Arbeitnow, Working Nomads, The Muse, We Work Remotely,
  Hacker News "Who's Hiring"). 9 sources.
- **`CONFIG_DRIVEN_SCRAPERS`** — Greenhouse and Lever job boards, where
  adding a new company is one line of config (`(board_token, company_name)`),
  not a new class. This is the Week 2/3 "scraper framework" payoff.

Run `python -m app.scraper.verify_sources` to check which configured
Greenhouse/Lever board tokens are still alive — companies migrate ATS
platforms or disable public boards without notice. `registry.py` has
comments tracking what's been pruned as dead. **There's a batch of
unverified Greenhouse tokens (`okta`, `zscaler`, `betterment`) still in the
list as of this writing — run `verify_sources.py` again and prune before
relying on the "50+ sources" number in a demo.**

`GET /job/scrape/meta` gives the live, authoritative source count rather
than counting by hand.

## Testing

```bash
pip install -r requirements.txt
python -m pytest app/tests/ -v
```

- `app/tests/scrapper/` — unit tests for individual scraper parsers and the
  cross-source dedup logic
- `app/tests/test_job_routes.py` — tests `/job/all`'s query param handling
  (search/filters/sort/pagination) against a fake `JobService`, so no real
  database is needed to run them

## Known gaps / next up

- No CI workflow runs tests automatically yet — nothing gates PRs on
  `pytest` passing
- The in-container scheduler is a plain daemon thread — fine for a single
  container, but if this ever runs as multiple replicas, every replica
  would scrape independently and you'd get duplicate runs. Not an issue
  at current scale; worth revisiting if that changes.
- Lever config-driven sources are down to just the demo company — nearly
  every real Lever board that was tried has gone dead; Greenhouse is
  carrying the "config-driven" story right now
