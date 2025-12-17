FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies for the MCP server
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server and supporting artifacts
COPY pingfederate_mcp_server.py /app/pingfederate_mcp_server.py
COPY swagger.json /app/swagger.json

# Run the MCP server over stdio
CMD ["python", "-u", "pingfederate_mcp_server.py"]
