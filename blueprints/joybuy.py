import logging
from http import HTTPStatus
from typing import Any

import niquests
from flask import jsonify, request
from flask.blueprints import Blueprint
from flask.wrappers import Response
from niquests.models import Response as NiquestsResponse
from niquests.sessions import Session

from api.joybuy.search_metadata import JdSearchMetadata, get_jd_metadata
from api.joybuy.search_products import JdProduct, get_jd_products
from api.utils import remove_query_param
from config import DEFAULT_PAGE_LIMIT, USER_AGENT

session: Session = niquests.Session(multiplexed=True)

headers: dict[str, str] = {
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Priority": "u=4",
    "RSC": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "TE": "trailers",
    "User-Agent": USER_AGENT,
}

joybuy_blueprint: Blueprint = Blueprint(name="joybuy", import_name=__name__)


@joybuy_blueprint.route(rule="/proxy", methods=["GET"])
def get_paged_products() -> tuple[Response | str, HTTPStatus]:
    encoded_url: str | None = request.args.get("url")
    page_limit: int | None = int(request.args.get("page_limit", DEFAULT_PAGE_LIMIT))

    if not encoded_url:
        return "Invalid input", HTTPStatus.BAD_REQUEST

    new_url: str = remove_query_param(url=encoded_url, param="page")

    logging.info(msg=f"Fetching initial URL: {new_url}")
    initial_response: NiquestsResponse = session.get(url=new_url, headers=headers)

    if not initial_response.text:
        return "No response from server", HTTPStatus.NO_CONTENT

    metadata: JdSearchMetadata | None = get_jd_metadata(initial_response.text)

    if not metadata:
        return "Invalid metadata", HTTPStatus.INTERNAL_SERVER_ERROR

    products: list[JdProduct] = []

    last_page: int = min(metadata.page.pageCount, page_limit)

    page_responses: list[NiquestsResponse] = []

    for page in range(1, last_page + 1):
        page_url: str = f"{new_url}&page={page}"

        logging.debug(msg=f"Querying page url: {page_url}")
        page_responses.append(session.get(url=page_url, headers=headers))

    for response in page_responses:
        if response.text:
            page_products: list[JdProduct] = get_jd_products(response.text)
            products.extend(page_products)

    products_dict: list[dict[str, Any]] = [product.model_dump() for product in products]

    return jsonify(products_dict), HTTPStatus.OK
