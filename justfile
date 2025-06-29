list:
    @just --list

format:
    uv run ruff check --select I --fix
    uv run ruff check . --fix

build-requirements:
    uv pip compile pyproject.toml -o requirements.txt

test:
    uv run pytest -x