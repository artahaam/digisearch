import logging

from qdrant_client.models import PointStruct

from digisearch.paths import LOG_DIR
from digisearch.qdrant.qdrant_retrieval import load_embeddings
from digisearch.qdrant.qdrant_init import get_client, COLLECTION_NAME, QdrantUnavailableError

logger = logging.getLogger('vecdb')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / 'vecdb.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


DEFAULT_UPSERT_BATCH_SIZE = 100


def _chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def upsert_embeddings(batch_size: int = DEFAULT_UPSERT_BATCH_SIZE, progress_callback=None) -> dict:

    embeddings = load_embeddings()
    total = len(embeddings)
    logger.info(f"{total} embeddings loaded")

    if total == 0:
        logger.info("No embeddings found; nothing to upsert.")
        return {"total": 0, "upserted": 0, "skipped": 0}

    client = get_client()  

    upserted = 0
    skipped = 0
    done = 0

    for batch in _chunked(embeddings, max(1, batch_size)):
        points = []
        for embedding in batch:
            product_id = embedding['product_id']
            vector = embedding['vector']
            try:
                points.append(
                    PointStruct(
                        id=int(product_id),
                        vector=vector,
                        payload={'url': f'https://www.digikala.com/product/{product_id}/'},
                    )
                )
            except (TypeError, ValueError) as e:
                skipped += 1
                logger.warning(f"Skipping embedding for product {product_id}: {e}")

        error = None
        if points:
            try:
                client.upsert(collection_name=COLLECTION_NAME, wait=True, points=points)
                upserted += len(points)
            except Exception as e:
                error = str(e)
                skipped += len(points)
                logger.error(f"Failed to upsert a batch of {len(points)} points: {e}")

        done += len(batch)
        if progress_callback:
            progress_callback(done, total, error)

    logger.info(f"Upsert finished: {upserted} upserted, {skipped} skipped, {total} total.")
    return {"total": total, "upserted": upserted, "skipped": skipped}


if __name__ == "__main__":
    try:
        stats = upsert_embeddings()
        logger.info(f"Qdrant embedding stage finished: {stats}")
    except QdrantUnavailableError as e:
        logger.error(str(e))
        raise
