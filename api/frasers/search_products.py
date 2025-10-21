import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile

from pydantic import BaseModel


class FrasersSizeVariant(BaseModel):
    description: str
    variantId: str


class FrasersProduct(BaseModel):
    image: str
    color: str
    brand: str
    name: str
    nameWithoutBrand: str
    sizeVariants: list[FrasersSizeVariant]
    price: float
    discountedPrice: float
    productUrl: str
    key: int
    category: list[str]
    activity: list[str]


class FrasersProductResult(BaseModel):
    query: str | None = None
    categoryCode: str | None = None
    currency: str | None = None
    locale: str | None = None
    products: list[FrasersProduct]


product_pattern: Pattern[str] = compile(
    pattern=r'({"(query|categoryCode)":".*,"products":.*"rolledupProducts":\[\]}\][^}\]]*})',
    flags=MULTILINE,
)


def get_fr_products(text: str) -> list[FrasersProduct]:
    logging.debug(msg="Extracting products")

    products: list[FrasersProduct] = []

    if not text:
        logging.warning(msg="Product input text missing")

        return products

    match: Match[str] | None = product_pattern.search(text)

    if not match:
        logging.warning(msg="Product match not found")

        return products

    try:
        payload = loads(s=match.group(1))
        pq: FrasersProductResult = FrasersProductResult(**payload)
        return pq.products
    except Exception as exc:
        logging.exception(msg=f"Failed to parse product payload: {exc}")
        return []
