import json
import re
from typing import Any
from urllib import error, parse, request

from mcp.server.fastmcp import FastMCP


API_BASE_URL = "http://127.0.0.1:5000"
MCP_HOST = "127.0.0.1"
MCP_PORT = 5001

GET_PATTERNS = (
    re.compile(r"^/api/health$"),
    re.compile(r"^/api/farmers(?:/\d+(?:/animals)?)?$"),
    re.compile(r"^/api/animals(?:/[A-Za-z0-9_-]+(?:/(?:vaccinations|health|labreports))?)?$"),
    re.compile(r"^/api/complaints(?:/[A-Za-z0-9_-]+)?$"),
    re.compile(r"^/api/dashboard/(?:summary|species|districts)$"),
)

POST_PATHS = {
    "/api/auth/login",
    "/api/login",
    "/api/ai/analyze",
    "/api/complaints",
}

mcp = FastMCP(
    "PashuRakshak API",
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
)


def _validate_get_path(path: str) -> str:
    parsed = parse.urlsplit(path)
    normalized_path = parsed.path or "/"
    if not any(pattern.fullmatch(normalized_path) for pattern in GET_PATTERNS):
        raise ValueError(f"GET path is not an allowed PashuRakshak endpoint: {normalized_path}")
    return normalized_path + (f"?{parsed.query}" if parsed.query else "")


def _validate_post_path(path: str) -> str:
    parsed = parse.urlsplit(path)
    normalized_path = parsed.path or "/"
    if normalized_path not in POST_PATHS:
        raise ValueError(f"POST path is not an allowed PashuRakshak endpoint: {normalized_path}")
    return normalized_path


def _send(method: str, path: str, body: bytes | None = None,
          content_type: str | None = None) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    http_request = request.Request(
        f"{API_BASE_URL}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with request.urlopen(http_request, timeout=30) as response:
            response_body = response.read().decode("utf-8")
            status_code = response.status
    except error.HTTPError as exc:
        response_body = exc.read().decode("utf-8")
        status_code = exc.code
    except error.URLError as exc:
        raise RuntimeError(f"Flask API is unreachable: {exc.reason}") from exc

    try:
        parsed_body = json.loads(response_body)
    except json.JSONDecodeError:
        parsed_body = response_body
    return {"status_code": status_code, "body": parsed_body}


@mcp.tool()
def api_get(path: str) -> dict[str, Any]:
    """Execute an allowed GET request against the local PashuRakshak Flask API."""
    return _send("GET", _validate_get_path(path))


@mcp.tool()
def api_post(path: str, json_body: dict[str, Any] | None = None,
             form_data: dict[str, str] | None = None) -> dict[str, Any]:
    """Execute an allowed JSON or form-data POST request against the local API."""
    normalized_path = _validate_post_path(path)
    if json_body is not None and form_data is not None:
        raise ValueError("Provide either json_body or form_data, not both")
    if form_data is not None:
        encoded_body = parse.urlencode(form_data).encode("utf-8")
        return _send("POST", normalized_path, encoded_body,
                     "application/x-www-form-urlencoded")
    encoded_body = json.dumps(json_body or {}).encode("utf-8")
    return _send("POST", normalized_path, encoded_body, "application/json")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")