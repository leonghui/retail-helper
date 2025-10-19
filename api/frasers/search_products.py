import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile
from typing import Optional

from pydantic import BaseModel


class SizeVariant(BaseModel):
    description: str
    variantId: str


class Product(BaseModel):
    image: str
    color: Optional[str] = None
    brand: str
    name: str
    nameWithoutBrand: Optional[str] = None
    sizeVariants: list[SizeVariant] = []
    price: Optional[float] = None
    discountedPrice: Optional[float] = None
    productUrl: Optional[str] = None
    key: str
    category: list[str] = []
    activity: list[str] = []


class ProductQuery(BaseModel):
    query: str
    products: list[Product]


product_pattern: Pattern[str] = compile(
    pattern=r'(^[0-9a-f]+\:\[\["\$","\$L\d+",null,)({"query":".*","products":.*"rolledupProducts":\[\]}\]})',
    flags=MULTILINE,
)


def get_products(text: str) -> list[Product]:
    logging.debug(msg="Extracting products")

    products: list[Product] = []

    if not text:
        logging.warning(msg="Product input text missing")

        return products

    match: Match[str] | None = product_pattern.search(text)

    if not match:
        logging.warning(msg="Product match not found")

        return products

    try:
        payload = loads(s=match.group(2))
        pq: ProductQuery = ProductQuery(**payload)
        return pq.products
    except Exception as exc:
        logging.exception(msg=f"Failed to parse product payload: {exc}")
        return []
