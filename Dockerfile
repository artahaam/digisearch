FROM python:3.12.3-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models

WORKDIR /app

RUN pip install torch \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -i https://mirror-pypi.runflare.com/simple

COPY pyproject.toml README.md ./
RUN pip install -r requirements.txt -i https://mirror-pypi.runflare.com/simple

COPY pyproject.toml .
COPY src ./src
RUN pip install --no-deps . -i https://mirror-pypi.runflare.com/simple

ENTRYPOINT ["python", "-m", "digisearch.pipeline.run"]
CMD ["--help"]