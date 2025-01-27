FROM python:3.12-slim AS build

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends mime-support \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv --no-cache-dir

COPY pyproject.toml ./

COPY src ./src

COPY LICENSE README.md ./

RUN uv sync --all-extras && uv build --wheel

# ----------------------------------------------------------------------------

FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=build /app/dist ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends mime-support curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install ./*.whl --no-cache-dir

COPY .env .env

COPY locales ./locales

RUN useradd -m user && chown -R user:user /app

USER user

CMD ["telegram-file-statistics-bot"]
