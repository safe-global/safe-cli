#!/usr/bin/env sh
trap 'docker compose --profile develop down' EXIT
docker compose --profile develop up --detach --wait anvil || exit 1
uv sync --frozen --group dev --all-extras || exit 1
uv run --frozen pytest
