from json import loads
import logging
from re import MULTILINE, Match, Pattern, compile

from api.bargainfox.search_metadata import BargainFoxProduct, BargainFoxResponse


product_pattern: Pattern[str] = compile(
    pattern=r'({"error":.+"total":\d+}})',
    flags=MULTILINE,
)


def get_bargainfox_products(text: str) -> list[BargainFoxProduct]:
    logging.debug(msg="Extracting products")

    products: list[BargainFoxProduct] = []

    if not text:
        logging.warning(msg="Product input text missing")

        return products

    match: Match[str] | None = product_pattern.search(text)

    if not match:
        logging.warning(msg="Product match not found")

        return products

    try:
        payload = loads(s=match.group(1))
        pq: BargainFoxResponse = BargainFoxResponse(**payload)
        return pq.result.data
    except Exception as exc:
        logging.exception(msg=f"Failed to parse product payload: {exc}")
        return []
