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


def remove_path_segment(url: str, segment: str) -> str:
    """
    Return ``url`` with every occurrence of the given *segment* removed from its path.

    - Decodes percent‑ and plus‑encoded input before processing.
    - Keeps the rest of the URL (scheme, netloc, query, fragment) unchanged.
    - Preserves the original ordering of path components.
    """
    logging.info(msg=f"Parsing input URL: {url}")

    # Decode any escaped characters so we work with the real path text
    decoded: str = unquote_plus(string=url)
    logging.debug(msg=f"Decoded URL: {decoded}")

    # Split the URL into components
    parsed: ParseResult = urlparse(url=decoded)

    # Remove the unwanted segment from the path
    # ``parsed.path`` is a string like "/search/.1/opt/page:1/sort:price/"
    # We split on '/' to work with individual parts, filter out the target,
    # then re‑join with '/' while preserving leading/trailing slashes.
    parts: list[str] = parsed.path.split(sep="/")
    filtered: list[str] = [p for p in parts if not p.startswith(segment)]

    # Re‑assemble the path, making sure we keep a leading slash
    new_path: str = "/".join(filtered)
    if not new_path.startswith("/"):
        new_path = "/" + new_path
    # Preserve a trailing slash if the original had one
    if parsed.path.endswith("/") and not new_path.endswith("/"):
        new_path += "/"

    # Build the final URL with the cleaned path
    result: str = urlunparse(components=parsed._replace(path=new_path))

    logging.debug(msg=f"Resulting URL: {result}")
    return result
