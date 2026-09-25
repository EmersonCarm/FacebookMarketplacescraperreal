"""
Edit this file to control what gets searched and what counts as "a good deal".
"""

# Facebook Marketplace location code, e.g. "carlisle-pa" or a numeric city id.
# Easiest way to find it: go to facebook.com/marketplace in a browser, search
# something, and copy the slug/id that shows up in the URL.
LOCATION = "carlisle-pa"

# Radius in miles around LOCATION.
RADIUS_MILES = 40

# Each entry is one saved search. `max_price` is a hard ceiling (listings above
# it are ignored entirely). `deal_ratio` controls the "good deal" alert: a
# listing is flagged as a deal if its price is <= deal_ratio * the median price
# of everything else you've seen so far for that same search term.
SEARCHES = [
    {"term": "3080", "max_price": 400, "deal_ratio": 0.75},
    {"term": "4070", "max_price": 500, "deal_ratio": 0.75},
    {"term": "ryzen 7", "max_price": 200, "deal_ratio": 0.75},
    {"term": "ddr4 32gb", "max_price": 80, "deal_ratio": 0.75},
    {"term": "ddr5 32gb", "max_price": 150, "deal_ratio": 0.75},
    {"term": "nvme ssd 1tb", "max_price": 70, "deal_ratio": 0.75},
    {"term": "9070", "max_price": 500, "deal_ratio": 0.75}
]

# How many prior listings for a given search term are needed before the
# deal_ratio comparison kicks in. Below this, you just get notified of every
# new listing so the price history can build up.
MIN_HISTORY_FOR_DEAL_CHECK = 5

# Poll interval, in minutes. Randomized within this range each cycle so
# requests don't look like a metronome. 60-120 matches your "every 1-2 hours".
POLL_INTERVAL_MIN_MINUTES = 60
POLL_INTERVAL_MAX_MINUTES = 120

# Where Playwright stores your logged-in Facebook session so you don't have
# to log in every run. Created by auth_setup.py.
AUTH_STATE_PATH = "auth_state.json"

DB_PATH = "listings.db"
LOG_PATH = "scraper.log"
