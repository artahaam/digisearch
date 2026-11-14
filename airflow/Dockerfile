FROM apache/airflow:3.3.2-python3.12 AS base

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10

USER root
RUN mkdir -p /opt/digisearch && chown airflow:0 /opt/digisearch
USER airflow
WORKDIR /opt/digisearch

COPY requirements.txt .
RUN --mount=type=bind,source=wheels,target=/tmp/wheels \
    pip install "apache-airflow==3.3.2" \
      --find-links /tmp/wheels \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -r requirements.txt \
      -i https://mirror-pypi.runflare.com/simple

COPY --chown=airflow:0 pyproject.toml README.md ./
COPY --chown=airflow:0 src ./src
RUN pip install --no-deps . -i https://mirror-pypi.runflare.com/simple

FROM base AS test
RUN pip install pytest -i https://mirror-pypi.runflare.com/simple
COPY --chown=airflow:0 tests ./tests
ENTRYPOINT ["pytest"]
CMD ["tests/dags", "-v"]