FROM python:3.12.3-slim AS base

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
      -i https://mirror-pypi.runflare.com/simple

COPY requirements.txt .
RUN --mount=type=bind,source=wheels,target=/tmp/wheels,rw=false \
    pip install \
      --find-links /tmp/wheels \
      -r requirements.txt \
      -i https://mirror-pypi.runflare.com/simple

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-deps . -i https://mirror-pypi.runflare.com/simple

FROM base AS test
RUN pip install pytest ruff -i https://mirror-pypi.runflare.com/simple
COPY tests ./tests
ENTRYPOINT ["pytest"]
CMD ["-v"]

FROM base AS prod
ENTRYPOINT ["python", "-m", "digisearch.pipeline.run"]
CMD ["--help"]