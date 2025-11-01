from typing import Literal


from flask.wrappers import Response


from http import HTTPStatus
import logging
from urllib.parse import unquote_plus

from flask import request
from flask.blueprints import Blueprint
from flask.wrappers import Response as FlaskResponse
import niquests
from niquests.models import Response as NiquestsResponse
from niquests.sessions import Session

session: Session = niquests.Session(disable_http1=True, multiplexed=True)

generic_blueprint: Blueprint = Blueprint(name="generic", import_name=__name__)


@generic_blueprint.route(rule="/proxy", methods=["GET"])
def get_paged_products() -> tuple[Response | str, HTTPStatus]:
    encoded_url: str | None = request.args.get("url")

    if not encoded_url:
        return "Invalid input", HTTPStatus.BAD_REQUEST

    new_url: str = unquote_plus(string=encoded_url)

    headers: dict[str, str] = dict[str, str](request.headers)
    headers.pop("Host")
    headers.pop("Accept-Encoding")

    logging.info(msg=f"Fetching URL: {new_url}")
    niquest_response: NiquestsResponse = session.get(url=new_url, headers=headers)

    mimetype: str = niquest_response.headers.get("Content-Type", "text/html")

    if niquest_response.content:
        return FlaskResponse(
            response=niquest_response.content,
            mimetype=mimetype,
        ), HTTPStatus(value=niquest_response.status_code)

    else:
        return "No response", HTTPStatus.NO_CONTENT
