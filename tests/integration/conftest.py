"""Fixtures for tests that talk to a REAL MongoDB and a REAL Qdrant.

Start them first:   docker compose up -d mongo qdrant
Run only these:     pytest -m integration -v
Skip them:          pytest -m "not integration"

If the services are not reachable the tests are skipped, unless the
environment variable REQUIRE_SERVICES=1 is set (as in CI), in which case they fail.
"""
import hashlib
import os

import numpy as np
import pytest
from pymongo import MongoClient
from qdrant_client import QdrantClient

from digisearch import config
from digisearch.database.client import get_db_client
from digisearch.database.setup import setup as setup_db
from digisearch.pipeline import store_embeddings
from digisearch.pipeline.store_products import save_product
from digisearch.qdrant.qdrant_init import get_qdrant_client


@pytest.fixture(scope="session")
def services():
    # Safety net: never run against a database/collection that isn't clearly a test one.
    if not (config.MONGO_DB.endswith("_test") and config.QDRANT_COLLECTION.endswith("_test")):
        pytest.exit(
            f"Refusing to run: MONGO_DB={config.MONGO_DB!r} / "
            f"QDRANT_COLLECTION={config.QDRANT_COLLECTION!r} are not test names.",
            returncode=2,
        )

    problems = []
    try:
        MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000).admin.command("ping")
    except Exception as e:
        problems.append(f"MongoDB at {config.MONGO_URI}: {e}")
    try:
        QdrantClient(url=config.QDRANT_URL, timeout=3).get_collections()
    except Exception as e:
        problems.append(f"Qdrant at {config.QDRANT_URL}: {e}")

    if problems:
        message = "integration services not reachable: " + "; ".join(problems)
        if os.getenv("REQUIRE_SERVICES"):
            pytest.fail(message)
        pytest.skip(message)


def _reset(recreate: bool) -> None:
    get_db_client().drop_database(config.MONGO_DB)

    raw = QdrantClient(url=config.QDRANT_URL, timeout=10)
    if raw.collection_exists(config.QDRANT_COLLECTION):
        raw.delete_collection(config.QDRANT_COLLECTION)
    get_qdrant_client.cache_clear()          # the cached client remembers the old collection

    if recreate:
        setup_db()                           # Mongo unique indexes
        get_qdrant_client()                  # recreates the collection + payload indexes


@pytest.fixture(autouse=True)
def clean_state(services):
    _reset(recreate=True)
    yield
    _reset(recreate=False)


@pytest.fixture
def qdrant():
    return QdrantClient(url=config.QDRANT_URL, timeout=10)


# ---------------------------------------------------------------------------
# A fake embedding model: deterministic vectors, no download, no GPU/CPU cost.
# ---------------------------------------------------------------------------


def _vector(text: str) -> np.ndarray:
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
    v = np.random.default_rng(seed).standard_normal(int(config.VECTOR_SIZE))
    return v / np.linalg.norm(v)


class FakeModel:
    def __init__(self):
        self.calls: list[list[str]] = []     # the documents of every encode() call
        self.fail_times = 0                  # make the next N encode() calls raise

    def encode(self, docs, batch_size=None, max_length=None):
        if self.fail_times > 0:
            self.fail_times -= 1
            raise RuntimeError("simulated model failure")
        self.calls.append(list(docs))
        return {"dense_vecs": np.array([_vector(d) for d in docs], dtype=np.float32)}


@pytest.fixture
def fake_model(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(store_embeddings, "get_embedding_model", lambda *a, **k: model)
    return model


@pytest.fixture
def add_product():
    """Store a product the same way the crawler does (save_product)."""

    def _add(product_id: int, **fields) -> dict:
        details = {
            "product_id": product_id,
            "product_title_en": f"Product {product_id}",
            "brand_title_en": "Acme",
            "product_categories": ["Cat"],
            "product_price": 1000,
            **fields,
        }
        save_product(details)
        return details

    return _add
