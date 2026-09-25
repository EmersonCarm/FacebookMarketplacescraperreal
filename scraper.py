"""
Scrapes one Marketplace search-results page and returns a list of dicts:
{listing_id, title, price, url, location}

NOTE ON SELECTORS: Facebook's markup for Marketplace changes periodically
and has no stable class names, so this relies on structural/text patterns
(links that look like /marketplace/item/<id>/) rather than CSS classes.
If Facebook redesigns the page, this is the part that will break first.
To debug, run `playwright codegen https://www.facebook.com/marketplace`
and click around to see what selectors currently match, or set
headless=False below and watch it load.
"""

import re
import logging
from urllib.parse import quote

from playwright.sync_api import sync_playwright, Page

import config

logger = logging.getLogger("scraper")

ITEM_URL_RE = re.compile(r"/marketplace/item/(\d+)")


def build_search_url(term: str) -> str:
    return (
        f"https://www.facebook.com/marketplace/{config.LOCATION}/search"
        f"?query={quote(term)}&radius={config.RADIUS_MILES}&exact=false"
    )


def extract_listings(page: Page, search_term: str) -> list[dict]:
    # Scroll a bit to trigger lazy-loading of more cards.
    for _ in range(4):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(800)

    anchors = page.locator("a[href*='/marketplace/item/']").all()
    results = []
    seen_ids = set()

    for a in anchors:
        href = a.get_attribute("href") or ""
        m = ITEM_URL_RE.search(href)
        if not m:
            continue
        listing_id = m.group(1)
        if listing_id in seen_ids:
            continue
        seen_ids.add(listing_id)

        # The card's visible text usually looks like:
        # "$350\nRTX 3080 10GB\nCarlisle, PA"
        text = a.inner_text().strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        price = None
        title = None
        location = None

        for line in lines:
            price_match = re.search(r"\$[\d,]+", line)
            if price_match and price is None:
                price = int(price_match.group(0).replace("$", "").replace(",", ""))

        # Title is usually the longest non-price line; location the last line.
        non_price_lines = [l for l in lines if not re.fullmatch(r"\$[\d,]+", l)]
        if non_price_lines:
            title = max(non_price_lines, key=len)
        if len(lines) >= 2:
            location = lines[-1]

        results.append(
            {
                "listing_id": listing_id,
                "title": title or "(unknown title)",
                "price": price,
                "url": f"https://www.facebook.com/marketplace/item/{listing_id}/",
                "location": location or "",
                "search_term": search_term,
            }
        )

    return results


def scrape_search(term: str, max_price: int, headless: bool = True) -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=config.AUTH_STATE_PATH)
        page = context.new_page()

        url = build_search_url(term)
        logger.info(f"Scraping: {url}")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        if "login" in page.url:
            logger.error(
                "Redirected to login page — your saved session has expired. "
                "Re-run auth_setup.py."
            )
            browser.close()
            return []

        listings = extract_listings(page, term)
        browser.close()

    return [l for l in listings if l["price"] is None or l["price"] <= max_price]
