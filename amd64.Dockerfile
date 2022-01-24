FROM python:3.9-alpine3.15

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="Roxedus"

COPY / /app

RUN apk add --no-cache --virtual=build-dependencies --update \
        gcc \
        musl-dev \
        python3-dev && \
    python3 -m pip install -r /app/requirements.txt && \
    apk del build-dependencies

WORKDIR /app

VOLUME [ "/data" ]

ENTRYPOINT [ "python3", "/app/launcher.py", "--data-directory", "/data" ]
