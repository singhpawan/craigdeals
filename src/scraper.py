"""Craigslist scraper.

Usage:
    python -m src.scraper [area] [num_posts]

Note: Craigslist periodically changes its HTML structure. If results drop to
zero, inspect the search page and update the CSS selectors in
_process_search_page and _process_row accordingly.
"""

import json
import logging
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
            "Mozilla/5.0 (compatible; CraigDealsBot/1.0)"
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

    def _find_lat_lon(self, soup: BeautifulSoup) -> tuple[Optional[float], Optional[float]]:
        tag = soup.find(id="map")
        if tag:
            return float(tag["data-latitude"]), float(tag["data-longitude"])
        return None, None

    def _find_date(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find(id="display-date") or soup.find("time")
        if tag:
            return tag.get("datetime") or tag.get_text(strip=True)
        return None

    # ------------------------------------------------------------------
    # Scraping logic
    # ------------------------------------------------------------------

    def _process_row(self, row) -> None:
        # Selectors cover both the legacy and modern Craigslist layouts
        price_tag = row.find("span", class_="result-price") or row.find("span", class_="price")
        title_tag = (
            row.find("a", class_="result-title")
            or (row.find("span", class_="pl") and row.find("span", class_="pl").find("a"))
        )
        if not price_tag or not title_tag:
            return

        title = title_tag.get_text(strip=True)
        price_text = price_tag.get_text(strip=True).replace("$", "").replace(",", "")
        if not price_text.isdigit():
            return
        price = int(price_text)

        href = title_tag.get("href", "")
        car_url = self.url_root + href if href.startswith("/") else href
        car_soup = self._get(car_url)
        if car_soup is None:
            return

        body_tag = car_soup.find(id="postingbody")
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
                pd.DataFrame(
                    [
                        {
                            "year": year, "model": model, "price": price,
                            "miles": miles, "lat": lat, "lon": lon,
                            "date": date, "area": self.area,
                            "title": title, "body": body,
                            "phone": phone, "image_count": image_count,
                            "url": href,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        logger.info("Scraped: %d %s %d mi @ $%d", year, model, miles, price)

    def _process_search_page(self, page_index: int) -> None:
        url = f"{self.url_root}/cta/index{page_index}.html"
        soup = self._get(url)
        if soup is None:
            return

        rows = soup.find_all("li", class_="result-row") or soup.find_all("p", class_="row")
        logger.info("Page %d: found %d rows", page_index, len(rows))

        for row in rows:
            try:
                self._process_row(row)
            except Exception:
                logger.exception("Unexpected error processing row")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape(self, num_posts: int) -> None:
        for page_index in range(0, num_posts, 100):
            logger.info("Scraping page index %d", page_index)
            self._process_search_page(page_index)
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
