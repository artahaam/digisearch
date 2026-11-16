FROM python:3.12.3-slim AS base

ARG PIP_INDEX_URL=https://pypi.org/simple

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    HF_HOME=/models

WORKDIR /app

RUN --mount=type=bind,source=wheels,target=/tmp/wheels,rw=false \
    pip install torch \
      --find-links /tmp/wheels \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -i ${PIP_INDEX_URL}

COPY requirements.txt .
RUN --mount=type=bind,source=wheels,target=/tmp/wheels,rw=false \
    pip install \
      --find-links /tmp/wheels \
      -r requirements.txt \
      -i ${PIP_INDEX_URL}

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-deps . -i ${PIP_INDEX_URL}

FROM base AS test
RUN pip install pytest ruff -i ${PIP_INDEX_URL}
COPY tests ./tests
ENTRYPOINT ["pytest"]
CMD ["-v"]

FROM base AS prod
ENTRYPOINT ["python", "-m", "digisearch.pipeline.run"]
CMD ["--help"]