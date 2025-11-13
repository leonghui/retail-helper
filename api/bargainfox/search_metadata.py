import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile

from pydantic import BaseModel


class BargainFoxProduct(BaseModel):
    id: int
    name: str
    short_title: str
    slug: str
    category_id: int
    main_rrp: float
    price: float
    sale_price: float
    stock: int
    discount_value: float
    percentage_discount: float


class BargainFoxResult(BaseModel):
    current_page: int
    data: list[BargainFoxProduct]
    last_page: int
    per_page: int
    to: int | None
    total: int


class BargainFoxResponse(BaseModel):
    error: bool
    status: int
    message: str
    result: BargainFoxResult


metadata_pattern: Pattern[str] = compile(
    pattern=r'({"error":.+"total":\d+}})',
    flags=MULTILINE,
)


def get_bargainfox_metadata(text: str) -> BargainFoxResult | None:
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
        pq: BargainFoxResponse = BargainFoxResponse(**payload)

        return pq.result
    except Exception as exc:
        logging.exception(msg=f"Failed to parse metadata: {exc}")
        return None
