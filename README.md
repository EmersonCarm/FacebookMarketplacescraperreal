# FB Marketplace Deal Watcher

Polls Facebook Marketplace searches on an interval, tracks what it's already
seen in SQLite, and flags/notifies when something is priced well below the
median for that search term.

## Setup (in VS Code)

1. Open this folder in VS Code (`File > Open Folder`).
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Edit `config.py`:
   - Set `LOCATION` to your area's Marketplace slug/id.
   - Add/edit entries in `SEARCHES` — one per part you're watching, with a
     `max_price` ceiling and `deal_ratio` (how far below median counts as
     a deal; 0.75 = 25% under the running median).
4. Log into Facebook once, headed, so the scraper can reuse your session:
   ```bash
   python auth_setup.py
   ```
5. Run it:
   ```bash
   python main.py
   ```
   It loops forever, scraping every 60–120 minutes (randomized — see
   `config.py`), logging to `scraper.log`, and firing a desktop notification
   for anything flagged as a deal.

## Notes / gotchas

- **This isn't sanctioned by Facebook.** Automated browsing of Marketplace
  is against their Terms of Service. Keep the interval slow (don't go below
  an hour), expect occasional login checkpoints, and treat this as a
  personal tool, not something to run at scale or share widely.
- **Selectors will break eventually.** `scraper.py` doesn't rely on CSS
  class names (Facebook's are auto-generated garbage) — it looks for
  `/marketplace/item/<id>/` links and parses the visible text of each card.
  If Facebook changes the layout and results come back empty or garbled,
  run `playwright codegen https://www.facebook.com/marketplace` to see the
  current structure and adjust `extract_listings()` in `scraper.py`.
- **Session expiring:** if logs show it got redirected to the login page,
  re-run `auth_setup.py`.
- **Running it continuously:** `main.py` is a long-running loop, meant to
  stay open in a terminal (or run under `tmux`/`screen` on a machine that's
  always on, or as a background service). If you'd rather trigger it via
  cron/Task Scheduler every N hours instead of an internal loop, change
  `scrape_search` calls to run once and exit, and let the OS scheduler
  handle timing instead.
- **First run for each search term** will have no price history, so
  `MIN_HISTORY_FOR_DEAL_CHECK` in `config.py` holds off deal-flagging until
  it's seen a handful of listings — otherwise everything looks like a deal
  against a sample size of one.

## Extending

- Swap `notifier.py`'s desktop notification for email/SMS/Discord webhook if
  you want alerts when you're not at your machine.
- Add a `min_price` per search to filter out obviously-fake $1 scam listings.
- The SQLite file (`listings.db`) is plain and queryable — `sqlite3
  listings.db "select * from listings order by first_seen desc limit 20;"`
  is a quick way to sanity-check what it's found.
