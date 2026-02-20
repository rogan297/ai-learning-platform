### STAGE 1: Build & Run
ARG DOCKER_REGISTRY=ghcr.io
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim


WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean


COPY pyproject.toml pyproject.toml
COPY .python-version .python-version

RUN uv sync --no-dev && uv cache clean


COPY orchestrator/ orchestrator/
COPY README.md README.md


ENV PYTHONPATH=/app
ENV PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uv", "run", "orchestrator/cli.py"]