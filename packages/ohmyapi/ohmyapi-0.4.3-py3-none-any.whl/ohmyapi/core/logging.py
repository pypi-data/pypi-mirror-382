import logging
import os
import sys


def setup_logging():
    """Configure unified logging for ohmyapi + FastAPI/Uvicorn."""
    log_level = os.getenv("OHMYAPI_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level, logging.INFO)

    # Root logger (affects FastAPI, uvicorn, etc.)
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Separate ohmyapi logger (optional)
    logger = logging.getLogger("ohmyapi")

    # Direct warnings/errors to stderr
    class LevelFilter(logging.Filter):
        def filter(self, record):
            # Send warnings+ to stderr, everything else to stdout
            if record.levelno >= logging.WARNING:
                record.stream = sys.stderr
            else:
                record.stream = sys.stdout
            return True

    for handler in logger.handlers:
        handler.addFilter(LevelFilter())

    logger.setLevel(level)
    return logger
