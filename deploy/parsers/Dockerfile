FROM python:3.10.6-slim as kbr_parser
LABEL version="0.0.1"
LABEL stage="beta"

COPY ./requirements/parser_requirements.txt /app/requirements.txt
WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r ./requirements.txt &&\
    apt --purge autoremove -y gcc

COPY ./parsers/kbr_parsers/. /app
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONPATH="${PYTHONPATH}:/app/kbr_parsers"
ENV PYTHONPATH="${PYTHONPATH}:/app/kbr_parsers/kbr_parsers"

ARG PARSER_NAME
ENV PARSER_NAME=${PARSER_NAME}
CMD scrapy crawl ${PARSER_NAME}