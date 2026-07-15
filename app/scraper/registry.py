from app.scraper.remotive import RemotiveScraper
from app.scraper.himalyas import HimalayasScraper
from app.scraper.jobicy import JobicyScraper
from app.scraper.remoteok import RemoteOkScraper
from app.scraper.arbeitnow import ArbeitnowScraper

SCRAPERS = [
    HimalayasScraper,
    JobicyScraper,
    RemoteOkScraper,
    RemotiveScraper,
    ArbeitnowScraper
]
