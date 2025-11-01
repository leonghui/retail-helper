from http import HTTPStatus
import logging
from urllib.parse import unquote_plus

from flask import request as FlaskRequest
from flask.blueprints import Blueprint
from flask.wrappers import Response
from flask.wrappers import Response as FlaskResponse
import niquests
from niquests.models import Response as NiquestsResponse
from niquests.sessions import Session

session: Session = niquests.Session(multiplexed=False)

generic_blueprint: Blueprint = Blueprint(name="generic", import_name=__name__)


@generic_blueprint.route(rule="/proxy", methods=["GET"])
def get_paged_products() -> tuple[Response | str, HTTPStatus]:
    encoded_url: str | None = FlaskRequest.args.get("url")
    verify_ssl: bool = FlaskRequest.args.get("ssl", "").lower() != "false"
    injected_host: str | None = FlaskRequest.args.get("host")

    if not encoded_url:
        return "Invalid input", HTTPStatus.BAD_REQUEST

    new_url: str = unquote_plus(string=encoded_url)

    headers: dict[str, str] = dict[str, str](FlaskRequest.headers)
    headers.pop("Host", "")
    headers.pop("Accept-Encoding", "")
    headers.pop("Referer", "")
    if injected_host:
        headers["Host"] = injected_host

    logging.info(msg=f"Fetching URL: {new_url}")
    niquest_response: NiquestsResponse = session.get(
        url=new_url, headers=headers, verify=verify_ssl
    )

    mimetype: str = niquest_response.headers.get("Content-Type", "text/html")

    if niquest_response.content:
        return FlaskResponse(
            response=niquest_response.content,
            mimetype=mimetype,
        ), HTTPStatus(value=niquest_response.status_code)

    else:
        return "No response", HTTPStatus.NO_CONTENT
