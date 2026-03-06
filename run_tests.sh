#/usr/bin/env sh
docker compose --profile develop up -d ganache
pip install -e .
pytest
docker compose down --profile develop
