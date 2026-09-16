from pathlib import Path
import gc
import json
import logging
from functools import lru_cache

from digisearch.paths import BGE_EMBEDDINGS_DIR, SEARCH_DOCUMENTS_PRODUCT_DIR, LOG_DIR


logger = logging.getLogger('embedding')
logger.setLevel(logging.DEBUG)

if not logger.handlers:  # avoid duplicate handlers on module re-exec (e.g. Streamlit's file watcher)
    file_handler = logging.FileHandler(LOG_DIR / 'process.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


DEFAULT_BATCH_SIZE = 8
DEFAULT_MAX_LENGTH = 1024
MODEL_NAME = "BAAI/bge-m3"


@lru_cache(maxsize=1)
def get_model(model_name: str = MODEL_NAME):

    from FlagEmbedding import BGEM3FlagModel

    logger.info(f"Loading embedding model '{model_name}' (this may take a while on first run)...")
    try:
        model = BGEM3FlagModel(model_name, use_fp16=True)
    except Exception:
        logger.exception(f"Failed to load embedding model '{model_name}'")
        raise
    logger.info(f"Embedding model '{model_name}' loaded.")
    return model


def count_documents() -> int:
    return sum(1 for _ in SEARCH_DOCUMENTS_PRODUCT_DIR.glob("*.txt"))


def embedding_exists(product_id):
    f = BGE_EMBEDDINGS_DIR / f"{product_id}.json"
    return f.exists()

def iter_pending_paths():
    for path in SEARCH_DOCUMENTS_PRODUCT_DIR.glob("*.txt"):
        if not embedding_exists(path.stem):
            yield path


def load_documents():
    documents = []
    for path in iter_pending_paths():
        doc = load_document(path)
        if doc is not None:
            documents.append(doc)
    return documents


def load_document(path: Path):
    product_id = path.stem
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning(f"Could not read search document {path}: {e}")
        return None
    return {"product_id": product_id, "text": text}


def _chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def _chunked_paths(paths, size):
    batch = []
    for p in paths:
        batch.append(p)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def generate_and_save_embeddings(
    paths,
    total: int,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_length: int = DEFAULT_MAX_LENGTH,
    progress_callback=None,
):

    model = get_model()
    done = 0
    saved = 0

    for path_batch in _chunked_paths(paths, max(1, batch_size)):
        # Read text for just this batch, not all documents up front.
        batch = [d for d in (load_document(p) for p in path_batch) if d is not None]
        if not batch:
            continue

        texts = [doc["text"] for doc in batch]
        try:
            encoded = model.encode(texts, batch_size=len(texts), max_length=max_length)
            vectors = encoded["dense_vecs"]
        except Exception as e:
            logger.error(f"Failed to encode a batch of {len(batch)} documents: {e}")
            done += len(batch)
            if progress_callback:
                progress_callback(done, total, error=str(e))
            continue

        saved += save_embeddings(zip(batch, vectors))

        done += len(batch)
        if progress_callback:
            progress_callback(done, total, error=None)

        # Explicitly drop references and reclaim memory before the next batch.
        del batch, texts, encoded, vectors
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

    return saved


def save_embeddings(doc_vector_pairs):
    saved = 0
    for doc, vector in doc_vector_pairs:
        output = {
            "product_id": doc["product_id"],
            "vector": vector.tolist() if hasattr(vector, "tolist") else list(vector),
        }

        output_path = BGE_EMBEDDINGS_DIR / f"{doc['product_id']}.json"
        try:
            output_path.write_text(
                json.dumps(output, indent=4, ensure_ascii=False),
                encoding="utf-8",
            )
            saved += 1
        except OSError as e:
            logger.warning(f"Could not save embedding for product {doc['product_id']}: {e}")

    return saved


def run(batch_size: int = DEFAULT_BATCH_SIZE, progress_callback=None) -> dict:

    paths = list(iter_pending_paths())
    total = len(paths)
    logger.info(f"{total} documents pending.")

    if total == 0:
        logger.info("No search documents found; nothing to embed.")
        return {"total": 0, "saved": 0, "failed": 0}

    saved = generate_and_save_embeddings(
        paths, total=total, batch_size=batch_size, progress_callback=progress_callback
    )
    logger.info(f"{saved} embeddings saved.")

    return {"total": total, "saved": saved, "failed": total - saved}


if __name__ == "__main__":
    stats = run()
    logger.info(f"Embedding stage finished: {stats}")