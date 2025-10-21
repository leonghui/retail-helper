import niquests
from flask import Response as FlaskResponse
from flask import request
from flask.blueprints import Blueprint
from flask.json import jsonify
from niquests.models import Response as NiquestResponse

idealo_blueprint: Blueprint = Blueprint(name="idealo", import_name=__name__)

user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0"

CUSTOM_HEADERS: dict[str, str] = {
    "User-Agent": user_agent,
    "Cookie": "xp_seed_s=f4ea2;",
}


# url = "https://www.idealo.co.uk/csr/api/v2/modules/searchResult?categoryId=4552&locale=en_GB&filters=102295028&sort=PRICE_ASC&itemStates=EXCLUDE_USED&query=64gb%20ddr5&priceFrom=0&priceTo=120"


@idealo_blueprint.route(rule="/", methods=["POST"])
def proxy():
    """
    Expected JSON payload:
    {
        "url": "https://www.idealo.co.uk/csr/api/v2/modules/searchResult?categoryId=1000&locale=en_GB",
        "body": {...},          # optional, sent as JSON
        "headers": {...}        # optional, extra headers to merge
    }
    """
    data = request.get_json()
    print(data)
    if not data or "url" not in data:
        return jsonify(error="Missing 'url' in JSON body"), 400

    target_url = data["url"]
    # Merge optional extra headers with the service‑specific ones
    extra_headers = data.get("headers", {})
    headers: dict = {**CUSTOM_HEADERS, **extra_headers}

    # Optional JSON body for the outbound request
    json_body = data.get("body")

    try:
        if json_body:
            resp: NiquestResponse = niquests.post(
                url=target_url, json=json_body, headers=headers, timeout=10
            )
        else:
            resp = niquests.get(url=target_url, headers=headers, timeout=10)
    except niquests.RequestException as e:
        return jsonify(error=f"Error contacting target: {e}"), 502

    return FlaskResponse(
        response=resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/octet-stream"),
    )
