"""Run this inside Docker to diagnose what Craigslist is returning.

    docker compose run --rm scraper python scripts/debug_scraper.py
"""
import re
import sys

import requests
from bs4 import BeautifulSoup

AREA = sys.argv[1] if len(sys.argv) > 1 else "sfbay"
URL = f"https://{AREA}.craigslist.org/search/cta?start=0"

LISTING_HREF_RE = re.compile(r"/\w{2,5}/ct[a-z]{1,3}/d/.+/\d+\.html")
PRICE_TEXT_RE = re.compile(r"^\$[\d,]+$")

session = requests.Session()
session.headers["User-Agent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

print(f"Fetching {URL} ...")
resp = session.get(URL, timeout=15)
print(f"Status: {resp.status_code}")
print(f"Content-Type: {resp.headers.get('content-type')}")
print(f"Response length: {len(resp.text)} chars")
print()

soup = BeautifulSoup(resp.text, "html.parser")

# --- Check for CAPTCHA / block page ---
title = soup.find("title")
print(f"Page <title>: {title.get_text() if title else 'none'}")
print()

# --- Count all <a> tags and matching ones ---
all_links = soup.find_all("a", href=True)
matching_links = soup.find_all("a", href=LISTING_HREF_RE)
print(f"Total <a> tags: {len(all_links)}")
print(f"Links matching listing href pattern: {len(matching_links)}")
print()

# --- Show first 5 matching hrefs ---
print("First 5 matching hrefs:")
for link in matching_links[:5]:
    print(f"  href : {link.get('href')}")
    print(f"  text : {link.get_text(strip=True)[:80]}")
    li = link.find_parent("li")
    if li:
        prices = [t.strip() for t in li.strings if PRICE_TEXT_RE.match(t.strip())]
        print(f"  price: {prices}")
    print()

# --- Show first 500 chars of raw HTML to spot blocks/CAPTCHAs ---
print("--- First 500 chars of raw HTML ---")
print(resp.text[:500])
print()

# --- Sample non-matching <a> hrefs to spot the real pattern ---
print("Sample of non-matching <a> hrefs (first 10):")
for link in all_links[:10]:
    print(f"  {link.get('href', '')[:100]}")
