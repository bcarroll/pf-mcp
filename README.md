- admin console: https://localhost:9999/pingfederate/app#/
- api docs: https://localhost:9999/pf-admin-api/api-docs/

## One-shot local stack (PingFederate + MCP)

Everything runs from compose in `docker/`—PingFederate and the MCP server come up together.

1) Put your license at `docker/PingFederate-12.3-Development.lic`.  
2) `cd docker && docker compose up --build`  
3) PingFederate: `https://localhost:9999` (admin) and `https://localhost:9031` (runtime).  
4) MCP server: auto-starts as `pingfederate-mcp` using `docker/mcp.Dockerfile` with env:
   - `PF_BASE_URL=https://pingfederate:9999/pf-admin-api/v1`
   - `PF_USERNAME=Administrator`
   - `PF_PASSWORD=2FederateM0re`
   - `PF_VERIFY_TLS=false`

## Manual MCP usage (optional)

## PingFederate container (docker/)

The `docker` folder holds the compose setup for a local PingFederate instance.

1. Drop your PingFederate license file in `docker/PingFederate-12.3-Development.lic`.
2. From `docker/`, build and start: `docker compose up --build`.
3. Admin console is on `https://localhost:9999`, runtime HTTPS on `https://localhost:9031`.
4. Default admin credentials match the image defaults (`Administrator` / `2FederateM0re` unless you changed them).

## MCP server

`pingfederate_mcp_server.py` exposes PingFederate over the Model Context Protocol using stdio.

### Setup

```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Run

```
PF_BASE_URL=https://localhost:9999/pf-admin-api/v1 \
PF_USERNAME=Administrator \
PF_PASSWORD=2FederateM0re \
PF_VERIFY_TLS=false \
python pingfederate_mcp_server.py
```

- `PF_BASE_URL`: Admin API base URL (default: `https://localhost:9999/pf-admin-api/v1`)
- `PF_USERNAME` / `PF_PASSWORD`: Admin credentials
- `PF_VERIFY_TLS`: Set to `true` only if you trust the TLS cert; defaults to `false` for the self-signed dev cert
- `PF_TIMEOUT`: Request timeout in seconds (default: `30`)

### Available MCP resources/tools

- Resources: `pf://admin-api/swagger` (local `swagger.json`), `pf://docker/compose` (`docker/compose.yml`)
- Tools: `pingfederate.get_version`, `pingfederate.list_admin_accounts`, `pingfederate.get_admin_account`, `pingfederate.call_admin_api`

### Run with Docker Compose

The compose setup also starts the MCP server alongside PingFederate:

```
cd docker
docker compose up --build
```

This builds `pingfederate-mcp` from `docker/mcp.Dockerfile`, copies `pingfederate_mcp_server.py` and `swagger.json`, installs `requirements.txt`, and runs the MCP server with:

- `PF_BASE_URL=https://pingfederate:9999/pf-admin-api/v1`
- `PF_USERNAME=Administrator`
- `PF_PASSWORD=2FederateM0re`
- `PF_VERIFY_TLS=false`
