FROM python:3.13-alpine

WORKDIR /app/

# Install uv — copy binary from official image, no pip bootstrap needed
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

RUN apk add build-base

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-dev --frozen --no-install-project

# Copy source and install the project itself (provides safe-cli / safe-creator entry points)
COPY src ./src
RUN uv sync --no-dev --frozen
