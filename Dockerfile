FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

RUN pip install --no-cache-dir uv

COPY src ./src
COPY mcp_server ./mcp_server

RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "mcp_server.http_server"]