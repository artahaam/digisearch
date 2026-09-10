import sys
import subprocess
import logging
from pathlib import Path
import argparse

from digisearch.paths import LOG_DIR, PROJECT_ROOT


logger = logging.getLogger("pipeline")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_DIR / "pipeline.log")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# -------------------------
# Scripts
# -------------------------

GET_CATEGORIES_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "get_categories.py"
)

CRAWLER_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "crawl.py"
)

LIST_PRODUCTS_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "processing" / "list_products.py"
)

CANONICALIZE_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "processing" / "canonicalize.py"
)

SEARCH_DOCUMENT_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "processing" / "search_document.py"
)

EMBEDDING_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "processing" / "embedding.py"
)

QDRANT_EMBEDDING_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "qdrant" / "qdrant_embedding.py"
)


QDRANT_RETRIEVAL_SCRIPT = (
    PROJECT_ROOT / "src" / "digisearch" / "qdrant" / "qdrant_retrieval.py"
)


def run_step(script_path: Path, step_name: str, args: list[str] | None = None) -> bool:
    if not script_path.exists():
        logger.error(
            f"Failed: {step_name} script not found at {script_path}"
        )
        return False

    logger.info(
        f"Starting Stage: {step_name} ({script_path.name})..."
    )

    cmd = [sys.executable, str(script_path)]

    if args:
        cmd.extend(args)

    try:
        subprocess.run(cmd, check=True)

        logger.info(
            f"Successfully finished Stage: {step_name}"
        )

        return True

    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error: {step_name} exited with "
            f"non-zero status code: {e.returncode}"
        )
        return False

    except Exception as e:
        logger.error(
            f"An unexpected error occurred while running "
            f"{step_name}: {e}"
        )
        return False



def run_retrieve_pipeline(args):

    logger.info("=== Starting Qdrant Retrieval Pipeline ===")

    get_retrieve_args = [
        f"query={args.query}",
    ]

    steps = [
        (QDRANT_RETRIEVAL_SCRIPT, "Retrieve Products"),
    ]

    for script, name in steps:
        success = run_step(script, name, args=get_retrieve_args)

        if not success:
            logger.critical(
                f"Pipeline aborted: {name} stage failed."
            )
            sys.exit(1)

    logger.info(
        "=== Product Retrieval Pipeline completed successfully! ==="
    )


def run_process_pipeline():

    logger.info("=== Starting Product Processing Pipeline ===")

    steps = [
        (LIST_PRODUCTS_SCRIPT, "List Products"),
        (CANONICALIZE_SCRIPT, "Canonicalize Products"),
        (SEARCH_DOCUMENT_SCRIPT, "Build Search Documents"),
        (EMBEDDING_SCRIPT, "Generate Embeddings"),
        (QDRANT_EMBEDDING_SCRIPT, "Qdrant Embedding")
    ]

    for script, name in steps:
        success = run_step(script, name)

        if not success:
            logger.critical(
                f"Pipeline aborted: {name} stage failed."
            )
            sys.exit(1)

    logger.info(
        "=== Product Processing Pipeline completed successfully! ==="
    )


def run_ingestion_pipeline(args):

    logger.info(
        "=== Starting Digikala Data Ingestion Pipeline ==="
    )

    get_category_args = [
        f"--filters={args.filters}",
        f"--ignore={args.ignore}",
        f"--output={args.output}",
        f"--id={args.id}",
    ]

    crawler_args = [
        f"--output={args.output}"
    ]

    success = run_step(
        GET_CATEGORIES_SCRIPT,
        "Category Discovery",
        args=get_category_args,
    )

    if not success:
        logger.critical(
            "Pipeline aborted: Category discovery stage failed."
        )
        sys.exit(1)

    success = run_step(
        CRAWLER_SCRIPT,
        "Data Crawling & Extraction",
        args=crawler_args,
    )

    if not success:
        logger.critical(
            "Pipeline aborted: Crawler stage failed."
        )
        sys.exit(1)

    logger.info(
        "=== Ingestion Pipeline completed successfully! ==="
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run DigiSearch pipelines."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # -------------------------
    # ingest
    # -------------------------

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Discover categories and crawl product data.",
    )

    ingest_parser.add_argument(
        "--filters",
        type=str,
        default="",
        help='Comma-separated filter keywords, e.g. "clothes,men,jeans"',
    )

    ingest_parser.add_argument(
        "--ignore",
        type=str,
        default="",
        help='Comma-separated keywords to ignore, e.g. "kids,women"',
    )

    ingest_parser.add_argument(
        "--output",
        type=str,
        default="categories.csv",
        help="Output CSV file name.",
    )
    ingest_parser.add_argument(
        "--id",
        type=str,
        default="",
        help="Comma-seperated category-IDs to keep.",
    )


    # -------------------------
    # process
    # -------------------------

    subparsers.add_parser(
        "process",
        help="Run the product processing pipeline.",
    )

    # -------------------------
    # retrieve
    # -------------------------


    search_parser = subparsers.add_parser(
        "search",
        help="Search for a product and retrieve the closest results.",
    )

    search_parser.add_argument(
        'query',
        type=str,
        help='Retrieval Query, e.g. "تی‌شرت نخی مناسب ورزش"'
    )
    search_parser.add_argument(
        "--topk",
        type=int,
        default=10,
        help='Retrieve top-k related products'
        )


    args = parser.parse_args()

    if args.command == "ingest":
        run_ingestion_pipeline(args)

    elif args.command == "process":
        run_process_pipeline()

    elif args.command == "search":
        run_retrieve_pipeline(args)


if __name__ == "__main__":
    main()