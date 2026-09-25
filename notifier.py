import logging

logger = logging.getLogger("notifier")


def notify(title: str, message: str):
    logger.info(f"NOTIFY: {title} | {message}")
    try:
        from plyer import notification

        notification.notify(title=title, message=message, timeout=15)
    except Exception as e:
        # Desktop notifications aren't critical to the scraper working —
        # fall back to just logging if plyer/the OS backend isn't available.
        logger.warning(f"Desktop notification failed ({e}); logged instead.")
