import logging
from urllib.parse import (
    ParseResult,
    parse_qs,
    unquote_plus,
    urlencode,
    urlparse,
    urlunparse,
)


def remove_query_param(url: str, param: str) -> str:
    """Return `url` with all occurrences of the named query parameter removed.

    - Decodes percent- and plus-encoded input before parsing.
    - Preserves other query parameters and their ordering where possible.
    """
    logging.info(msg=f"Parsing input URL: {url}")
    decoded: str = unquote_plus(string=url)
    logging.debug(msg=f"Decoded URL: {decoded}")

    parsed: ParseResult = urlparse(url=decoded)
    params: dict[str, list[str]] = parse_qs(qs=parsed.query, keep_blank_values=True)

    params.pop(param, None)

    new_query: str = urlencode(query=params, doseq=True)
    result: str = urlunparse(components=parsed._replace(query=new_query))

    logging.debug(msg=f"Resulting URL: {result}")
    return result
