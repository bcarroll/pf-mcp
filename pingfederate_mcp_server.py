from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import anyio
import httpx
from mcp.server.fastmcp import Context, FastMCP


def _env_flag(name: str, default: bool) -> bool:
    """Parse boolean-ish environment variables."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off", ""}


PF_BASE_URL = os.getenv("PF_BASE_URL", "https://localhost:9999/pf-admin-api/v1").rstrip("/")
PF_USERNAME = os.getenv("PF_USERNAME", "Administrator")
PF_PASSWORD = os.getenv("PF_PASSWORD", "2FederateM0re")
PF_VERIFY_TLS = _env_flag("PF_VERIFY_TLS", False)
PF_TIMEOUT = float(os.getenv("PF_TIMEOUT", "30"))

ROOT = Path(__file__).resolve().parent
SWAGGER_PATH = ROOT / "swagger.json"
COMPOSE_PATH = ROOT / "docker" / "compose.yml"

app = FastMCP(
    name="pingfederate-mcp",
    instructions=(
        "Interact with a local PingFederate instance (see docker/compose.yml). "
        "Use PF_BASE_URL, PF_USERNAME, PF_PASSWORD, PF_VERIFY_TLS, and PF_TIMEOUT to configure connectivity."
    ),
)


async def _api_request(
    path: str,
    *,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    context: Context | None = None,
) -> dict[str, Any] | str:
    """Perform a PingFederate Admin API request with basic auth."""
    normalized_path = path if path.startswith("/") else f"/{path}"
    auth = httpx.BasicAuth(PF_USERNAME, PF_PASSWORD)

    async with httpx.AsyncClient(
        base_url=PF_BASE_URL,
        auth=auth,
        verify=PF_VERIFY_TLS,
        timeout=PF_TIMEOUT,
    ) as client:
        response = await client.request(method.upper(), normalized_path, params=params, json=payload)

    body_text = response.text
    content_type = response.headers.get("content-type", "")

    if context:
        context.debug(
            f"PingFederate {method.upper()} {normalized_path} -> {response.status_code} "
            f"(verify_tls={PF_VERIFY_TLS})"
        )

    if response.is_error:
        raise RuntimeError(f"PingFederate responded with {response.status_code}: {body_text}")

    if "json" in content_type:
        try:
            return response.json()
        except json.JSONDecodeError:
            pass

    return body_text


@app.resource(
    "pf://admin-api/swagger",
    name="PingFederate Admin API spec",
    description="Local swagger.json bundled with the project for offline reference.",
    mime_type="application/json",
)
def pingfederate_swagger() -> str:
    return SWAGGER_PATH.read_text(encoding="utf-8")


@app.resource(
    "pf://docker/compose",
    name="PingFederate docker compose",
    description="docker/compose.yml used to run PingFederate locally.",
    mime_type="text/yaml",
)
def pingfederate_compose() -> str:
    return COMPOSE_PATH.read_text(encoding="utf-8")


@app.tool(
    name="pingfederate.get_version",
    description="Return PingFederate version information from /version.",
)
async def get_version(context: Context) -> dict[str, Any] | str:
    return await _api_request("/version", context=context)


@app.tool(
    name="pingfederate.list_admin_accounts",
    description="List native administrative accounts.",
)
async def list_admin_accounts(context: Context) -> dict[str, Any] | str:
    return await _api_request("/administrativeAccounts", context=context)


@app.tool(
    name="pingfederate.get_admin_account",
    description="Fetch a specific native administrative account by username.",
)
async def get_admin_account(username: str, context: Context) -> dict[str, Any] | str:
    return await _api_request(f"/administrativeAccounts/{username}", context=context)


@app.tool(
    name="pingfederate.call_admin_api",
    description=(
        "Call an arbitrary PingFederate Admin API path (relative to PF_BASE_URL). "
        "Supports GET/POST/PUT/PATCH/DELETE with optional params and JSON payload."
    ),
)
async def call_admin_api(
    path: str,
    method: str = "GET",
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    context: Context | None = None,
) -> dict[str, Any] | str:
    return await _api_request(path, method=method, params=params, payload=payload, context=context)


if __name__ == "__main__":
    anyio.run(app.run_stdio_async)
