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
    ("anthropic", "Anthropic"),
    ("airbnb", "Airbnb"),
    ("stripe", "Stripe"),
    ("doordash", "DoorDash"),
    ("robinhood", "Robinhood"),
    ("coinbase", "Coinbase"),
    ("gitlab", "GitLab"),
    ("figma", "Figma"),
    ("discord", "Discord"),
    ("cloudflare", "Cloudflare"),
    ("asana", "Asana"),
    ("notion", "Notion"),
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
    ("docusign", "DocuSign"),
    ("twitch", "Twitch"),
    ("credit-karma", "Credit Karma"),
    ("webflow", "Webflow"),
]

LEVER_COMPANIES = [
    ("leverdemo", "Lever Demo"),
    ("netlify", "Netlify"),
    ("eventbrite", "Eventbrite"),
    ("plaid", "Plaid"),
    ("branch", "Branch"),
    ("carta", "Carta"),
    ("segment", "Segment"),
    ("attentive", "Attentive"),
    ("grammarly", "Grammarly"),
    ("scaleai", "Scale AI"),
    ("clever", "Clever"),
    ("loom", "Loom"),
    ("close", "Close"),
    ("clearbit", "Clearbit"),
    ("getaround", "Getaround"),
    ("framer", "Framer"),
    ("shield-ai", "Shield AI"),
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
