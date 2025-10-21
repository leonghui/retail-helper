import logging
from json import loads
from re import MULTILINE, Match, Pattern, compile

from pydantic import BaseModel


class ArgosAttributes(BaseModel):
    productId: str
    sainId: str
    name: str
    brand: str
    price: float
    avgRating: float
    reviewsCount: int
    wasPrice: float | None
    wasText: str | None
    deliverable: bool
    reservable: bool
    freeDelivery: bool
    deliveryCost: float
    specialOfferText: str
    specialOfferCount: int
    buyable: bool
    imageURL: str = ""


class ArgosProduct(BaseModel):
    id: str
    attributes: ArgosAttributes


class ArgosPageProps(BaseModel):
    productData: list[ArgosProduct]


class ArgosProductResult(BaseModel):
    pageProps: ArgosPageProps
    analyticsCookie: str


product_pattern: Pattern[str] = compile(
    pattern=r'({"pageProps":{"productData":.+"analyticsCookie":"ecomm"})',
    flags=MULTILINE,
)


def get_argos_products(text: str) -> list[ArgosProduct]:
    logging.debug(msg="Extracting products")

    products: list[ArgosProduct] = []

    if not text:
        logging.warning(msg="Product input text missing")

        return products

    match: Match[str] | None = product_pattern.search(text)

    if not match:
        logging.warning(msg="Product match not found")

        return products

    try:
        payload = loads(s=match.group(1))
        pq: ArgosProductResult = ArgosProductResult(**payload)
        return pq.pageProps.productData
    except Exception as exc:
        logging.exception(msg=f"Failed to parse product payload: {exc}")
        return []
