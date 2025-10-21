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

DEFAULT_PAGE_LIMIT: int = int(os.environ.get("DEFAULT_PAGE_LIMIT", "5"))

USER_AGENT: str = os.environ.get(
    "USER_AGENT",
    "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
)

DEFAULT_HEADERS: dict[str, str] = {
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "TE": "trailers",
    "User-Agent": USER_AGENT,
}