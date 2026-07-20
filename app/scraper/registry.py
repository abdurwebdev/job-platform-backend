from functools import partial
from app.scraper.remotive import RemotiveScraper
from app.scraper.himalyas import HimalayasScraper
from app.scraper.jobicy import JobicyScraper
from app.scraper.remoteok import RemoteOkScraper
from app.scraper.arbeitnow import ArbeitnowScraper
from app.scraper.nomads import WorkingNomadsScraper
from app.scraper.themuse import TheMuseScraper
from app.scraper.wwremotely import WeWorkRemotelyScraper
from app.scraper.hackernews import HackerNewsHiringScraper
from app.scraper.lever import LeverScraper
from app.scraper.greenhouse import GreenhouseScraper

# --- Bespoke, one-off scrapers (one class per site) -------------------
DIRECT_SCRAPERS = [
    HimalayasScraper,
    JobicyScraper,
    RemoteOkScraper,
    RemotiveScraper,
    ArbeitnowScraper,
    WorkingNomadsScraper,
    TheMuseScraper,
    WeWorkRemotelyScraper,
    HackerNewsHiringScraper,
]

# --- Config-driven sources ---------------------------------------------
# This is the payoff of the scraper framework: every company below is a
# NEW source added with one line of config, not one new class.
#
# NOTE: board tokens/slugs can rot (companies migrate ATS, disable public
# boards, or rebrand). Run `python -m app.scraper.verify_sources` and prune
# any that come back empty/404 before you rely on the count in a demo.

GREENHOUSE_COMPANIES = [
    # --- confirmed alive as of the last verify_sources.py run ---------
    ("anthropic", "Anthropic"),
    ("airbnb", "Airbnb"),
    ("stripe", "Stripe"),
    ("robinhood", "Robinhood"),
    ("coinbase", "Coinbase"),
    ("gitlab", "GitLab"),
    ("figma", "Figma"),
    ("discord", "Discord"),
    ("cloudflare", "Cloudflare"),
    ("asana", "Asana"),
    ("pinterest", "Pinterest"),
    ("lyft", "Lyft"),
    ("affirm", "Affirm"),
    ("dropbox", "Dropbox"),
    ("elastic", "Elastic"),
    ("gusto", "Gusto"),
    ("webflow", "Webflow"),
    ("instacart", "Instacart"),
    ("brex", "Brex"),
    ("mixpanel", "Mixpanel"),
    ("twitch", "Twitch"),
    # removed as dead per last verify_sources.py run:
    # doordash, notion, docusign, credit-karma

    # --- confirmed alive per your latest verify_sources.py run --------
    ("samsara", "Samsara"),
    ("roblox", "Roblox"),
    ("reddit", "Reddit"),
    ("squarespace", "Squarespace"),
    ("faire", "Faire"),
    ("flexport", "Flexport"),
    ("verkada", "Verkada"),
    ("checkr", "Checkr"),
    ("mongodb", "MongoDB"),
    ("circleci", "CircleCI"),
    ("launchdarkly", "LaunchDarkly"),
    ("datadog", "Datadog"),
    ("newrelic", "New Relic"),
    ("fastly", "Fastly"),
    ("twilio", "Twilio"),
    ("amplitude", "Amplitude"),
    ("cultureamp", "Culture Amp"),
    # removed as dead per your latest verify_sources.py run:
    # databricks, retool, ramp, rippling, sourcegraph, hashicorp,
    # grafana-labs, toasttab, benchling, deel, vanta, gong, postmanlabs,
    # confluent, snowflake, mondaycom, miro, canva, github, sendgrid,
    # zendesk, outreach

    # --- UNVERIFIED, second batch: run verify_sources.py ONE more time
    # tonight and prune any DEAD ones from this batch too. You're at 49
    # confirmed sources without these — too close to "50+" to risk it,
    # so this batch exists purely as a buffer.
    ("okta", "Okta"),
    ("zscaler", "Zscaler"),
    ("betterment", "Betterment"),
]

LEVER_COMPANIES = [
    # --- confirmed alive as of the last verify_sources.py run ---------
    ("leverdemo", "Lever Demo"),
    # removed as dead (first pruning pass):
    # netlify, eventbrite, plaid, branch, carta, segment, attentive,
    # grammarly, scaleai, clever, loom, close, clearbit, getaround,
    # framer, shield-ai
    # removed as dead (second pruning pass, your latest verify run):
    # qualtrics, box, betterup, kraken, chainalysis
    #
    # Lever's public postings API has very few companies still on it
    # publicly — Greenhouse is genuinely the better config-driven source
    # for scale right now. Worth saying this plainly in the demo rather
    # than padding this list with more guesses.
]

# de-dupe accidental repeats in the config lists themselves
GREENHOUSE_COMPANIES = list(dict.fromkeys(GREENHOUSE_COMPANIES))
LEVER_COMPANIES = list(dict.fromkeys(LEVER_COMPANIES))

CONFIG_DRIVEN_SCRAPERS = [
    partial(GreenhouseScraper, board_token=token, company_name=name)
    for token, name in GREENHOUSE_COMPANIES
] + [
    partial(LeverScraper, company_slug=slug, company_name=name)
    for slug, name in LEVER_COMPANIES
]

SCRAPERS = DIRECT_SCRAPERS + CONFIG_DRIVEN_SCRAPERS
