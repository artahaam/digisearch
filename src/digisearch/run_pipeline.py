import sys
import subprocess
import logging
from pathlib import Path
import argparse

from digisearch.paths import DATA_DIR, LOG_DIR, PROJECT_ROOT

logger = logging.getLogger("pipeline")
logger.setLevel(logging.DEBUG)


GET_CATEGORIES_SCRIPT = PROJECT_ROOT / "src" / "digisearch" / "get_categories.py"
CRAWLER_SCRIPT = PROJECT_ROOT/ "src" / "digisearch" / "crawl.py" 



file_handler = logging.FileHandler(LOG_DIR / 'pipeline.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def run_step(script_path: Path, step_name: str, args: list = []) -> bool:

    if not script_path.exists():
        logger.error(f"Failed: {step_name} script not found at {script_path}")
        return False

    logger.info(f"Starting Stage: {step_name} ({script_path.name})...")

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)


       
    try:
        result = subprocess.run(cmd, check=True, text=True)
        logger.info(f"Successfully finished Stage: {step_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error: {step_name} exited with non-zero status code: {e.returncode}")
        return False
    
    except Exception as e:
        logger.error(f"An unexpected error occurred while running {step_name}: {e}")
        return False

def main():
    logger.info("=== Starting Digikala Data Ingestion Pipeline ===")
    
    parser = argparse.ArgumentParser(description="Run the Digikala data pipeline.")
    parser.add_argument(
        '--filters',
        type=str,
        required=False,
        default="",
        help='Comma-separated list of filter keywords, e.g. "clothes,men,jeans"'
    )
    parser.add_argument(
    '--ignores',
    type=str,
    required=False,
    default="",
    help='Comma-separated list of filter keywords, e.g. "clothes,men,jeans"'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=False,
        default="categories.csv",
        help='Output CSV file name, e.g. "clothes_categories.csv"'
    )
    args = parser.parse_args()


    get_category_args = [
        f'--filters={args.filters}',
        f'--ignores={args.ignores}',
        f'--output={args.output}'
    ]

    crawler_args = [
        f'--output={args.output}'
    ]

    success = run_step(GET_CATEGORIES_SCRIPT, "Category Discovery", args=get_category_args)
    if not success:
        logger.critical("Pipeline aborted: Category discovery stage failed. Leaving crawler untouched.")
        sys.exit(1)


    success = run_step(CRAWLER_SCRIPT, "Data Crawling & Extraction", args=crawler_args)
    if not success:
        logger.critical("Pipeline finished with errors: Crawler stage failed.")
        sys.exit(1)
        
    logger.info("=== Pipeline completed successfully! ===")

if __name__ == "__main__":
    main()
