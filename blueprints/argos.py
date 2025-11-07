import logging
from http import HTTPStatus
from typing import Any

import niquests
from flask import jsonify, request
from flask.blueprints import Blueprint
from flask.wrappers import Response
from niquests.models import Response as NiquestsResponse
from niquests.sessions import Session

from api.argos.search_metadata import ArgosProductMetadata, get_argos_metadata
from api.argos.search_products import ArgosProduct, get_argos_products
from api.utils import remove_path_segment, is_valid_url
from config import DEFAULT_HEADERS, DEFAULT_PAGE_LIMIT

ARGOS_ALLOWED_DOMAINS: list[str] = ["argos.co.uk", "www.argos.co.uk"]

session: Session = niquests.Session(multiplexed=True)

headers: dict[str, str] = DEFAULT_HEADERS | {
    "Priority": "u=0",
    "RSC": "1",
}

argos_blueprint: Blueprint = Blueprint(name="argos", import_name=__name__)


@argos_blueprint.route(rule="/proxy", methods=["GET"])
def get_paged_products() -> tuple[Response | str, HTTPStatus]:
    encoded_url: str | None = request.args.get("url")
    page_limit: int | None = int(request.args.get("page_limit", DEFAULT_PAGE_LIMIT))

    if not encoded_url or not is_valid_url(
        url=encoded_url, allowed_domains=ARGOS_ALLOWED_DOMAINS
    ):
        return "Invalid input", HTTPStatus.BAD_REQUEST

    new_url: str = remove_path_segment(url=encoded_url, segment="page")

    logging.info(msg=f"Fetching initial URL: {new_url}")
    initial_response: NiquestsResponse = session.get(url=new_url, headers=headers)

    if not initial_response.text:
        return "No response from server", HTTPStatus.NO_CONTENT

    metadata: ArgosProductMetadata | None = get_argos_metadata(initial_response.text)

    if not metadata:
        return "Invalid metadata", HTTPStatus.INTERNAL_SERVER_ERROR

    products: list[ArgosProduct] = []

    last_page: int = min(metadata.totalPages, page_limit) if metadata.totalPages else 0

    page_responses: list[NiquestsResponse] = []

    for page in range(1, last_page + 1):
        page_url: str = new_url if page == 1 else f"{new_url.rstrip('/')}/page:{page}/"

        logging.debug(msg=f"Querying page url: {page_url}")
        page_responses.append(session.get(url=page_url, headers=headers))

    for response in page_responses:
        if response.text:
            page_products: list[ArgosProduct] = get_argos_products(response.text)
            products.extend(page_products)

    products_dict: list[dict[str, Any]] = [product.model_dump() for product in products]

    return jsonify(products_dict), HTTPStatus.OK
