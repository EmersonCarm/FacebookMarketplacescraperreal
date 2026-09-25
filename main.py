import logging
import os
import random
import time

import config
import storage
from scraper import scrape_search
from notifier import notify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(config.LOG_PATH), logging.StreamHandler()],
)
logger = logging.getLogger("main")


def run_cycle():
    for search in config.SEARCHES:
        term = search["term"]
        max_price = search["max_price"]
        deal_ratio = search["deal_ratio"]

        try:
            listings = scrape_search(term, max_price)
        except Exception as e:
            logger.exception(f"Scrape failed for '{term}': {e}")
            continue

        logger.info(f"'{term}': {len(listings)} listings under ${max_price}")

        for listing in listings:
            if not storage.is_new(listing["listing_id"]):
                continue

            history = storage.price_history(term)
            med = storage.median_price(term)
            is_deal = (
                listing["price"] is not None
                and med is not None
                and len(history) >= config.MIN_HISTORY_FOR_DEAL_CHECK
                and listing["price"] <= deal_ratio * med
            )

            storage.save_listing(
                listing["listing_id"],
                term,
                listing["title"],
                listing["price"],
                listing["url"],
                listing["location"],
            )

            price_str = f"${listing['price']}" if listing["price"] is not None else "?"
            if is_deal:
                notify(
                    f"Deal: {term}",
                    f"{listing['title']} — {price_str} (median ~${med:.0f})\n{listing['url']}",
                )
                logger.info(f"DEAL FLAGGED: {listing['title']} {price_str} {listing['url']}")
            else:
                logger.info(f"New listing: {listing['title']} {price_str} {listing['url']}")


def main():
    storage.init_db()

    if not os.path.exists(config.AUTH_STATE_PATH):
        logger.error(
            f"No saved session found at {config.AUTH_STATE_PATH}. "
            "Run `python auth_setup.py` first."
        )
        return

    while True:
        logger.info("Starting scrape cycle")
        run_cycle()

        wait_minutes = random.uniform(
            config.POLL_INTERVAL_MIN_MINUTES, config.POLL_INTERVAL_MAX_MINUTES
        )
        logger.info(f"Cycle done. Sleeping {wait_minutes:.1f} minutes.")
        time.sleep(wait_minutes * 60)


if __name__ == "__main__":
    main()
