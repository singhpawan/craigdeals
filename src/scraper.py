from __future__ import annotations

"""Craigslist scraper.

Usage:
    python -m src.scraper [area] [num_posts]

Craigslist periodically changes its HTML. The current selectors target the
structure as of mid-2024. If results drop to zero, fetch a search page and
inspect the listing link href pattern and price element.
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .db import get_engine
from .utils import find_miles, find_model, find_phone, find_year

logger = logging.getLogger(__name__)

MODELS_FILE = Path(__file__).parent.parent / "models.json"

# Matches modern Craigslist listing hrefs:
# /eby/cto/d/hayward-2017-honda/7941905565.html
_LISTING_HREF_RE = re.compile(r"/\w{2,5}/ct[a-z]{1,3}/d/.+/\d+\.html")
_PRICE_TEXT_RE = re.compile(r"^\$[\d,]+$")

# Modern Craigslist paginates in steps of 120
PAGE_SIZE = 120


class Scraper:
    def __init__(self, area: str) -> None:
        self.area = area
        self.url_root = f"https://{area}.craigslist.org"
        self.models: set[str] = {
            m["name"] for m in json.loads(MODELS_FILE.read_text())
        }
        self.df = pd.DataFrame(
            columns=[
                "year", "model", "price", "miles",
                "lat", "lon", "date", "area",
                "title", "body", "phone", "image_count", "url",
            ]
        )
        self._session = requests.Session()
        self._session.headers["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get(self, url: str) -> Optional[BeautifulSoup]:
        try:
            resp = self._session.get(url, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as exc:
            logger.warning("GET %s failed: %s", url, exc)
            return None

    def _find_price_in_li(self, li) -> Optional[int]:
        """Find the price from any text node inside a listing <li>."""
        for text in li.strings:
            t = text.strip()
            if _PRICE_TEXT_RE.match(t):
                return int(t.replace("$", "").replace(",", ""))
        return None

    def _find_lat_lon(self, soup: BeautifulSoup) -> tuple[Optional[float], Optional[float]]:
        tag = soup.find(id="map")
        if tag and tag.get("data-latitude"):
            return float(tag["data-latitude"]), float(tag["data-longitude"])
        return None, None

    def _find_date(self, soup: BeautifulSoup) -> Optional[str]:
        # <time datetime="2024-05-01 10:30"> or <span>Posted 2024-05-01 10:30</span>
        time_tag = soup.find("time")
        if time_tag:
            return time_tag.get("datetime") or time_tag.get_text(strip=True)
        for span in soup.find_all("span"):
            text = span.get_text(strip=True)
            if text.startswith("Posted"):
                return text.removeprefix("Posted").strip()
        return None

    # ------------------------------------------------------------------
    # Scraping logic
    # ------------------------------------------------------------------

    def _process_listing(self, href: str, title: str, price: int) -> None:
        car_url = href if href.startswith("http") else self.url_root + href
        car_soup = self._get(car_url)
        if car_soup is None:
            return

        body_tag = car_soup.find(id="postingbody") or car_soup.find(
            "section", {"class": lambda c: c and "postingbody" in c}
        )
        body = body_tag.get_text(strip=True) if body_tag else ""

        model = find_model(title, self.models) or find_model(body, self.models)
        if not model:
            return

        miles = find_miles(title) or find_miles(body)
        year = find_year(title) or find_year(body)
        if not miles or not year:
            return

        lat, lon = self._find_lat_lon(car_soup)
        date = self._find_date(car_soup)
        phone = find_phone(body) or find_phone(title)

        thumbs = car_soup.find("div", id="thumbs")
        image_count = len(thumbs.find_all("img")) if thumbs else 0

        self.df = pd.concat(
            [
                self.df,
                pd.DataFrame([{
                    "year": year, "model": model, "price": price,
                    "miles": miles, "lat": lat, "lon": lon,
                    "date": date, "area": self.area,
                    "title": title, "body": body,
                    "phone": phone, "image_count": image_count,
                    "url": href,
                }]),
            ],
            ignore_index=True,
        )
        logger.info("Scraped: %d %s %d mi @ $%d", year, model, miles, price)

    def _process_search_page(self, start: int) -> None:
        # Modern Craigslist search URL with pagination offset
        url = f"{self.url_root}/search/cta?start={start}"
        soup = self._get(url)
        if soup is None:
            return

        # All listing links match the href pattern regardless of class names
        links = soup.find_all("a", href=_LISTING_HREF_RE)
        logger.info("Page start=%d: found %d listing links", start, len(links))

        seen: set[str] = set()
        for link in links:
            href = link.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)

            title = link.get_text(strip=True)
            if not title:
                continue

            # Price is a sibling text node inside the enclosing <li>
            li = link.find_parent("li")
            price = self._find_price_in_li(li) if li else None
            if not price:
                continue

            try:
                self._process_listing(href, title, price)
            except Exception:
                logger.exception("Unexpected error processing listing %s", href)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape(self, num_posts: int) -> None:
        for start in range(0, num_posts, PAGE_SIZE):
            logger.info("Scraping page start=%d", start)
            self._process_search_page(start)
        logger.info("Scraping complete — %d listings collected", len(self.df))

    def save(self) -> None:
        engine = get_engine()
        self.df.to_sql("scraped", engine, if_exists="append", index=False)
        logger.info("Saved %d rows to 'scraped'", len(self.df))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    area = sys.argv[1] if len(sys.argv) > 1 else "sfbay"
    num_posts = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    scraper = Scraper(area)
    scraper.scrape(num_posts)
    scraper.save()
