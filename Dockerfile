FROM python:3.10-alpine

WORKDIR /app/
RUN apk add build-base
COPY setup.* README.md ./
COPY safe_cli ./safe_cli
RUN pip install .
