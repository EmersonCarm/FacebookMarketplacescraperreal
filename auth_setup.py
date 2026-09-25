"""
Run this ONCE, by hand: `python auth_setup.py`

It opens a real (visible) browser window, you log into Facebook manually
(including any 2FA/checkpoint), then press Enter in the terminal and it
saves your session to config.AUTH_STATE_PATH. main.py reuses that session
so it doesn't have to log in on every scheduled run.

Re-run this any time Facebook logs the session out (you'll see login-page
content start showing up in the logs instead of listings).
"""

from playwright.sync_api import sync_playwright
import config


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.facebook.com/login")

        print("Log into Facebook in the opened browser window.")
        print("Once you're fully logged in and see your feed/marketplace, "
              "come back here and press Enter.")
        input()

        context.storage_state(path=config.AUTH_STATE_PATH)
        print(f"Session saved to {config.AUTH_STATE_PATH}")
        browser.close()


if __name__ == "__main__":
    main()
