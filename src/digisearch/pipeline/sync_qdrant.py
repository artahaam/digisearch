import logging

from qdrant_client.models import PointIdsList

from digisearch.database.client import get_db, get_db_client
from digisearch.qdrant.qdrant_init import QDRANT_COLLECTION, get_qdrant_client

log = logging.getLogger(__name__)


def qdrant_point_ids(page_size: int = 1000):
    client = get_qdrant_client()
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=page_size,
            offset=offset,
            with_payload=False,
            with_vectors=False,
        )
        yield from (p.id for p in points)
        if offset is None:
            break


def prune_orphans(batch_size: int = 500, dry_run: bool = False,
                  force: bool = False) -> dict:
    products = get_db()["products"]
    mongo_ids = {d["product_id"] for d in products.find({}, {"product_id": 1, "_id": 0})}
    qdrant_ids = set(qdrant_point_ids())

    orphans = sorted(qdrant_ids - mongo_ids)
    missing = len(mongo_ids - qdrant_ids)

    client = get_db_client()
    stats = {
        "mongo_server": client.admin.command("serverStatus")["host"],
        "mongo_db": products.database.name,
        "mongo": len(mongo_ids),
        "qdrant": len(qdrant_ids),
        "orphans": len(orphans),
        "deleted": 0,
        "missing_in_qdrant": missing,
    }

    if qdrant_ids and not force:
        if not mongo_ids:
            raise RuntimeError("MongoDB has no products; refusing to prune (use --force)")

    if missing:
        log.warning("%d products are in MongoDB but not in Qdrant; "
                    "run `embed --force` to rebuild them", missing)

    if dry_run:
        log.info("dry run: %s", stats)
        log.info("would delete %d orphan points: %s", len(orphans), orphans[:20])
        return stats

    client = get_qdrant_client()
    for i in range(0, len(orphans), batch_size):
        chunk = orphans[i:i + batch_size]
        client.delete(collection_name=QDRANT_COLLECTION,
                      points_selector=PointIdsList(points=chunk), wait=True)
        stats["deleted"] += len(chunk)
    log.info("done: %s", stats)
    return stats