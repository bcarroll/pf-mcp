- admin console: https://localhost:9999/pingfederate/app#/
- api docs: https://localhost:9999/pf-admin-api/api-docs/

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
- Tools: `pf.get_version`, `pf.list_admin_accounts`, `pf.get_admin_account`, `pf.call_admin_api`

### Quick start in VS Code

If you use an MCP-aware VS Code setup (e.g., Copilot MCP), the repo includes `.vscode/mcp.json` to start this server automatically:

1. Ensure PingFederate is running (`cd docker && docker compose up --build` with a license in `docker/PingFederate-12.3-Development.lic`).
2. Open the repo in VS Code; the MCP client will spawn `pingfederate_mcp_server.py` with the env in `.vscode/mcp.json` (PF host/user/password and TLS settings).
3. In the MCP panel, select `pingfederate-mcp-server`, then use the resources/tools listed above.
