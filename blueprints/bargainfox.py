from http import HTTPStatus
import logging
from typing import Any

from flask import jsonify, request
from flask.blueprints import Blueprint
from flask.wrappers import Response
import niquests
from niquests.models import Response as NiquestsResponse
from niquests.sessions import Session

from api.bargainfox.search_metadata import BargainFoxResult, get_bargainfox_metadata
from api.bargainfox.search_model import BargainFoxSearchModel, BargainFoxSearchParams
from api.bargainfox.search_products import BargainFoxProduct, get_bargainfox_products
from api.utils import get_search_params, is_valid_url
from config import DEFAULT_HEADERS, DEFAULT_PAGE_LIMIT, TIMEOUT

BARGAINFOX_ALLOWED_DOMAINS: list[str] = ["bargainfox.com"]

session: Session = niquests.Session(multiplexed=True)

headers: dict[str, str] = DEFAULT_HEADERS | {
    "Next-Action": "bcff783ffff24f29da1c2661721efdeca7b0d827",
    "Priority": "u=4",
}

bargainfox_blueprint: Blueprint = Blueprint(name="bargainfox", import_name=__name__)


@bargainfox_blueprint.route(rule="/proxy", methods=["GET"])
def get_paged_products() -> tuple[Response | str, HTTPStatus]:
    encoded_url: str | None = request.args.get("url")
    page_limit: int | None = int(request.args.get("page_limit", DEFAULT_PAGE_LIMIT))

    if not encoded_url or not is_valid_url(
        url=encoded_url, allowed_domains=BARGAINFOX_ALLOWED_DOMAINS
    ):
        return "Invalid input", HTTPStatus.BAD_REQUEST

    params: dict[str, list[str]] = get_search_params(encoded_url)

    url: str = encoded_url

    search_params: BargainFoxSearchParams = BargainFoxSearchParams(
        searchText=params.get("searchText", ["+"])[0],
        sort_by=params.get("sort_by", ["most_recent"])[0],
    )

    initial_payload: list[dict[str, Any]] = [
        BargainFoxSearchModel(pageNumber=1, searchParams=search_params).model_dump()
    ]

    logging.info(msg=f"Fetching initial URL: {url}")
    initial_response: NiquestsResponse = session.post(
        url=url, headers=headers, json=initial_payload, timeout=TIMEOUT
    )

    if not initial_response.ok:
        return "Error from server", HTTPStatus.INTERNAL_SERVER_ERROR

    if not initial_response.text:
        return "No response from server", HTTPStatus.NO_CONTENT

    metadata: BargainFoxResult | None = get_bargainfox_metadata(initial_response.text)

    if not metadata:
        return "Invalid metadata", HTTPStatus.INTERNAL_SERVER_ERROR

    products: list[BargainFoxProduct] = []

    last_page: int = min(metadata.last_page, page_limit) if metadata.total else 0

    page_responses: list[NiquestsResponse] = []

    for page in range(0, last_page):
        page_payload: list[dict[str, Any]] = [
            BargainFoxSearchModel(
                pageNumber=page + 1, searchParams=search_params
            ).model_dump()
        ]

        logging.debug(msg=f"Querying page {page + 1} for url: {url}")
        page_responses.append(
            session.post(url=url, headers=headers, json=page_payload, timeout=TIMEOUT)
        )

    for response in page_responses:
        if response.ok and response.text:
            page_products: list[BargainFoxProduct] = get_bargainfox_products(
                response.text
            )
            products.extend(page_products)

    products_dict: list[dict[str, Any]] = [product.model_dump() for product in products]

    return jsonify(products_dict), HTTPStatus.OK
