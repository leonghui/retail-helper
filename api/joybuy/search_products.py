import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile

from pydantic import BaseModel


class Content(BaseModel):
    wareName: str
    imageUrl: str
    realPrice: float
    originalPrice: float | None


class JdProduct(BaseModel):
    skuId: int
    content: Content
    wareInStock: int


class JdProductQuery(BaseModel):
    k: str | None = None
    correctionWord: str | None = None
    paragraphs: list[JdProduct]


product_pattern: Pattern[str] = compile(
    pattern=r'({"k":".*"paragraphs":\[{"skuId":.*"contractDeviceVO":[^}\]]+}\]})',
    flags=MULTILINE,
)


def get_jd_products(text: str) -> list[JdProduct]:
    logging.debug(msg="Extracting products")

    products: list[JdProduct] = []

    if not text:
        logging.warning(msg="Page input text missing")

        return products

    match: Match[str] | None = product_pattern.search(text)

    if not match:
        logging.warning(msg="Product match not found")

        return products

    try:
        payload = loads(s=match.group(1))
        pq: JdProductQuery = JdProductQuery(**payload)
        return pq.paragraphs
    except Exception as exc:
        logging.exception(msg=f"Failed to parse product payload: {exc}")
        return []
