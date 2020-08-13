FROM python:3.8-alpine3.12

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="Roxedus" \
    org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="ProgBott" \
    org.label-schema.description="Discord bot for å håndtere hjelpsomme folk" \
    org.label-schema.url="https://norskprogrammering.no/" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/Roxedus/ProgBott" \
    org.label-schema.version=$VERSION \
    org.label-schema.schema-version="1.0"

COPY / /app

RUN apk add --no-cache --virtual=build-dependencies --update \
        gcc \
        musl-dev \
        python-dev && \
    python3 -m pip install -r /app/requirements.txt && \
    apk del build-dependencies

WORKDIR /app

VOLUME [ "/data" ]

ENTRYPOINT [ "python3", "/app/launcher.py", "--data-directory", "/data" ]