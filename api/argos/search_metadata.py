import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile

from pydantic import BaseModel


class ArgosProductMetadata(BaseModel):
    appliedSort: str
    currentPage: int
    numberOfResults: int
    pageSize: int
    totalPages: int | None = None


class ArgosSearchResult(BaseModel):
    productMetadata: ArgosProductMetadata
    templateType: str
    categoryName: str


metadata_pattern: Pattern[str] = compile(
    pattern=r'({"isAvifImageFmt":.+"includeCitrusAds":(?:true|false|null)})',
    flags=MULTILINE,
)


def get_argos_metadata(text: str) -> ArgosProductMetadata | None:
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
        pq: ArgosSearchResult = ArgosSearchResult(**payload)

        return pq.productMetadata
    except Exception as exc:
        logging.exception(msg=f"Failed to parse metadata: {exc}")
        return None
