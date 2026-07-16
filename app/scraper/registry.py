from app.scraper.remotive import RemotiveScraper
from app.scraper.himalyas import HimalayasScraper
from app.scraper.jobicy import JobicyScraper
from app.scraper.remoteok import RemoteOkScraper
from app.scraper.arbeitnow import ArbeitnowScraper
from app.scraper.nomads import WorkingNomadsScraper
from app.scraper.themuse import TheMuseScraper
from app.scraper.wwremotely import WeWorkRemotelyScraper
from app.scraper.hackernews import HackerNewsHiringScraper

SCRAPERS = [
    HimalayasScraper,
    JobicyScraper,
    RemoteOkScraper,
    RemotiveScraper,
    ArbeitnowScraper,
    WorkingNomadsScraper,
    TheMuseScraper,
    WeWorkRemotelyScraper,
    HackerNewsHiringScraper
]
