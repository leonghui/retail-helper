import logging
from http import HTTPStatus
from typing import Any

import niquests
from flask import jsonify, request
from flask.blueprints import Blueprint
from flask.wrappers import Response
from niquests.models import Response as NiquestsResponse
from niquests.sessions import Session

from api.frasers.search_metadata import SearchMetadata, get_metadata
from api.frasers.search_products import Product, get_products
from api.utils import remove_query_param

PAGE_LIMIT = 3

session: Session = niquests.Session(multiplexed=True)

headers: dict[str, str] = {"RSC": "1"}

frasers_blueprint: Blueprint = Blueprint(name="frasers", import_name=__name__)


@frasers_blueprint.route(rule="/proxy", methods=["GET"])
def get_paged_products() -> tuple[Response | str, HTTPStatus]:
    encoded_url: str | None = request.args.get("url")

    if not encoded_url:
        return "Invalid input", HTTPStatus.BAD_REQUEST

    new_url: str = remove_query_param(url=encoded_url, param="dcp")

    logging.info(msg=f"Fetching initial URL: {new_url}")
    initial_response: NiquestsResponse = session.get(url=new_url, headers=headers)

    if not initial_response.text:
        return "No response from server", HTTPStatus.NO_CONTENT

    metadata: SearchMetadata | None = get_metadata(initial_response.text)

    if not metadata:
        return "Invalid metadata", HTTPStatus.INTERNAL_SERVER_ERROR

    products: list[Product] = []

    last_page: int = min(metadata.pageCount, PAGE_LIMIT)

    for page in range(1, last_page + 1):
        page_url: str = f"{new_url}&dcp={page}"

        logging.info(msg=f"Querying page url: {page_url}")
        page_response: NiquestsResponse = session.get(url=page_url, headers=headers)

        if not page_response.text:
            logging.warning(msg=f"No response for page {page}, stopping pagination")
            break

        page_products: list[Product] = get_products(page_response.text)

        products.extend(page_products)

    products_dict: list[dict[str, Any]] = [product.model_dump() for product in products]

    return jsonify(products_dict), HTTPStatus.OK
