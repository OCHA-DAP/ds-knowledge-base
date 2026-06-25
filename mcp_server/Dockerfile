# Container for the hosted (Streamable HTTP) deployment.
# The image bundles the KB content so the KB tools have something to read.
# DSCI_AZ_* read creds and KB_MCP_ENABLE_INFRA are injected at runtime (Azure
# app settings / secrets) — never baked into the image.
FROM python:3.11-slim

WORKDIR /app

COPY mcp_server/requirements.txt /app/mcp_server/requirements.txt
RUN pip install --no-cache-dir -r /app/mcp_server/requirements.txt

# Bundle the KB content + the server package.
COPY . /app

ENV KB_ROOT=/app \
    KB_MCP_TRANSPORT=streamable-http \
    HOST=0.0.0.0 \
    PORT=8000 \
    PGSSLMODE=require
EXPOSE 8000

CMD ["python", "-m", "mcp_server.server"]
