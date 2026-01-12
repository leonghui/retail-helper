import logging
from http import HTTPStatus
from urllib.parse import unquote_plus

import niquests
from flask import request as FlaskRequest
from flask.blueprints import Blueprint
from flask.wrappers import Response
from flask.wrappers import Response as FlaskResponse
from niquests.models import Response as NiquestsResponse
from niquests.sessions import Session

from config import TIMEOUT

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
    try:
        niquest_response: NiquestsResponse = session.get(
            url=new_url, headers=headers, verify=verify_ssl, timeout=TIMEOUT
        )

        mimetype: str = niquest_response.headers.get("Content-Type", "text/html")

        if niquest_response.content:
            return FlaskResponse(
                response=niquest_response.content,
                mimetype=mimetype,
            ), HTTPStatus(value=niquest_response.status_code)

        else:
            return "No response", HTTPStatus.NO_CONTENT
    except niquests.exceptions.ConnectionError:
        error_msg: str = f"Error fetching URL:  {new_url}"
        logging.error(msg=error_msg)
        return error_msg, HTTPStatus.INTERNAL_SERVER_ERROR
