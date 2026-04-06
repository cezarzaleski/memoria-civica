FROM node:20-bookworm-slim

WORKDIR /app
ENV MCP_BRASIL_RUNTIME=python \
    PATH="/opt/mcp-brasil/bin:${PATH}" \
    PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates python3 python3-venv \
  && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/mcp-brasil \
  && /opt/mcp-brasil/bin/pip install --no-cache-dir --upgrade pip \
  && /opt/mcp-brasil/bin/pip install --no-cache-dir mcp-brasil truststore

COPY package.json package-lock.json tsconfig.json ./
COPY apps ./apps
COPY packages ./packages

RUN npm ci --include=dev

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:' + (process.env.PORT || '3000') + '/health').then((response) => { if (!response.ok) process.exit(1); }).catch(() => process.exit(1))"

CMD ["npm", "run", "api:start"]
