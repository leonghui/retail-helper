import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile

from pydantic import BaseModel


class SearchMetadata(BaseModel):
    currency: str
    indexName: str
    pageCount: int
    pageNumber: int
    products: str
    productsCount: int
    queryId: str
    relativeReference: str


metadata_pattern: Pattern[str] = compile(
    pattern=r'({"currency":".*"})(\]$)',
    flags=MULTILINE,
)


def get_metadata(text: str) -> SearchMetadata | None:
    logging.debug(msg="Extracting search metadata")

    if not text:
        logging.warning(msg="Metadata input text missing")
        return None

    match: Match[str] | None = metadata_pattern.search(text)

    if not match:
        logging.warning(msg="Metadata match not found")
        return None

    try:
        payload = loads(s=match.group(1))
        return SearchMetadata(**payload)
    except Exception as exc:
        logging.exception(msg=f"Failed to parse metadata: {exc}")
        return None
