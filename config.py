import os

LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

LOG_FORMAT = "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(filename)-12s | %(funcName)15s | %(message)s"

LOG_CONFIG = {
    "version": 1,
    "formatters": {"default": {"format": LOG_FORMAT, "datefmt": "%Y-%m-%d %H:%M:%S"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {"root": {"handlers": ["console"], "level": LOG_LEVEL}},
}

FRASERS_PAGE_LIMIT: int = int(os.environ.get("FRASERS_PAGE_LIMIT", "5"))
