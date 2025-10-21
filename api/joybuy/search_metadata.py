import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile

from pydantic import BaseModel


class JdResultPage(BaseModel):
    pageCount: int
    pageIndex: int
    pageSize: int


class JdSearchMetadata(BaseModel):
    orgSkuCount: int
    resultCut: int
    resultShowCount: int
    resultCount: int
    page: JdResultPage


metadata_pattern: Pattern[str] = compile(
    pattern=r'("data":{"head":{"summary":)({"orgSkuCount".*"pageSize":\d+}})',
    flags=MULTILINE,
)


def get_jd_metadata(text: str) -> JdSearchMetadata | None:
    logging.debug(msg="Extracting search metadata")

    if not text:
        logging.warning(msg="Metadata input text missing")
        return None

    match: Match[str] | None = metadata_pattern.search(text)

    if not match:
        logging.warning(msg="Metadata match not found")
        return None

    try:
        payload = loads(s=match.group(2))
        return JdSearchMetadata(**payload)
    except Exception as exc:
        logging.exception(msg=f"Failed to parse metadata: {exc}")
        return None
