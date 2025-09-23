FROM python:3.13-alpine

WORKDIR /app/
RUN apk add build-base
COPY setup.* README.md pyproject.toml ./
COPY src ./src
RUN pip install -U pip && pip install .
