import argparse
import logging
from digisearch.logging_config import setup_logging
from digisearch.pipeline.store_categories import store_categories
from digisearch.pipeline.store_products import store
from digisearch.services.get_categories import fetch_categories_dict
from digisearch.pipeline.store_embeddings import embed_pending
from digisearch.pipeline.sync_qdrant import prune_orphans
from digisearch.database.setup import setup as setup_db

log = logging.getLogger(__name__)


def refresh_categories() -> int:
    n = store_categories(fetch_categories_dict())
    log.info("categories written: %d", n)
    return n


def main() -> None:
    p = argparse.ArgumentParser()

    p.add_argument("stage", choices=["setup", "categories", "products", "embed", "prune"])
    p.add_argument("--category", type=int, nargs="*", help="limit products to these category ids")
    p.add_argument("--max-age-hours", type=float, default=None, help="skip products fetched more recently (0 = refetch all)")
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--force", action="store_true", help="embed: re-embed everything; prune: skip safety checks")
    p.add_argument("--dry-run", action="store_true", help="prune: only report what would be deleted")

    args = p.parse_args()

    setup_logging()
    if args.stage == "setup":
        setup_db()
    elif args.stage == "categories":
        refresh_categories()
    elif args.stage == "products":
        kwargs = {} if args.max_age_hours is None else {"max_age_hours": args.max_age_hours}
        store(args.category, **kwargs)
    elif args.stage == "prune":
        prune_orphans(dry_run=args.dry_run, force=args.force)
    else:
        embed_pending(batch_size=args.batch_size, limit=args.limit, force=args.force)

if __name__ == "__main__":
    main()