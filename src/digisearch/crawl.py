import requests
import json
import csv
from pathlib import Path
import logging
import time
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field
import argparse
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TaskID,
)

from digisearch.paths import PROJECT_ROOT

def find_all_keys(obj, target_key) -> list:
    results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == target_key:
                results.append(value)

            results.extend(find_all_keys(value, target_key))

    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_all_keys(item, target_key))

    return results


# BASE_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_ROOT 
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CATEGORY_DIR = RAW_DIR / "category"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
LOG_DIR = BASE_DIR / "logs"

for directory in (RAW_DIR, CATEGORY_DIR, CHECKPOINT_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)


logger = logging.getLogger('crawler')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_DIR / 'crawler.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.debug("Directories set up finished.")


@dataclass
class CrawlerState:
    total_categories: int = 0
    categories_done: int = 0
    category_id: str = "-"
    category_title: str = "-"
    pages_total: int = 0
    pages_done: int = 0
    products_total: int = 0
    products_done: int = 0
    pages_saved: int = 0
    products_saved: int = 0
    errors: int = 0
    skipped: int = 0
    started_at: float = field(default_factory=time.monotonic)
    events: deque = field(default_factory=lambda: deque(maxlen=6))

    @property
    def elapsed(self) -> str:
        return f"{time.monotonic() - self.started_at:.0f}s"

    def log(self, message: str) -> None:
        self.events.appendleft(f"[{self.elapsed}] {message}")


def render_dashboard(state: CrawlerState, progress: Progress) -> Panel:
    overview = Table(show_header=False, box=None, padding=(0, 1))
    overview.add_column(style="bold", justify="right")
    overview.add_column(style="cyan")
    overview.add_row("Category", f"{state.category_id} · {state.category_title}")
    overview.add_row("Page", f"{state.pages_done}/{state.pages_total}")
    overview.add_row("Products", f"{state.products_done}/{state.products_total}")
    overview.add_row("Pages saved", str(state.pages_saved))
    overview.add_row("Products saved", str(state.products_saved))
    overview.add_row("Errors / skipped", f"{state.errors} / {state.skipped}")
    overview.add_row("Elapsed", state.elapsed)
    overview.add_row("Categories", f"{state.categories_done}/{state.total_categories}")

    events = Table(show_header=False, box=None, padding=(0, 1))
    events.add_column(style="dim", no_wrap=True)
    for line in state.events:
        events.add_row(line)
    if not state.events:
        events.add_row(Text("waiting for events...", style="dim"))

    return Panel(
        Group(
            progress,
            Panel(overview, title="Overview", border_style="blue"),
            Panel(events, title="Events", border_style="green"),
        ),
        title="DigiSearch Crawler Dashboard",
        border_style="bold magenta",
    )


def main() -> None:


    parser = argparse.ArgumentParser(description="crawling categories")
    parser.add_argument(
        '--output',
        type=str,
        required=False,
        default="categories.csv",
        help='Output CSV file name, e.g. "clothes_categories.csv"'
    )
    args = parser.parse_args()

    file_name = args.output

    console = Console()

    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console,
    )

    state = CrawlerState()

    # checkpoints
    checkpoint_file = CHECKPOINT_DIR / "checkpoint.csv"
    file_exists = checkpoint_file.exists()

    if not file_exists:
        with open(checkpoint_file, "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["cat_id", "page", "date"])

    try:
        with open(checkpoint_file, "r", encoding="utf-8") as csv_file:
            logger.debug("checkpoint.csv opened.")
            reader = csv.DictReader(csv_file)
            checkpoint = list(reader)[-1]
            category_checkpoint = checkpoint.get("cat_id", None)
            category_page_checkpoint = checkpoint.get("page", 1) 
            logger.debug(f"category_checkpoint : {category_checkpoint}, page_checkpoint: {category_page_checkpoint}")

    except:
        logger.debug("could not open checkpoint.csv, setting the checkpoints to default")
        category_checkpoint = None
        category_page_checkpoint = 1

    category_file_input = file_name

    with open(category_file_input, "r", encoding="utf-8") as csv_file:
        logger.debug(f"{category_file_input} opened.")
        reader = csv.DictReader(csv_file)

        rows = list(reader)
        logger.info(rows)

        categories = []

        for r in rows:
            categories.append(r["id"])

        if category_checkpoint is not None:
            try:
                category_start_range = categories.index(category_checkpoint)
            except:
                logger.warning("could not find checkpoints, getting all categories.")
                category_start_range = 0
        else:
            category_start_range = 0

        # continue from category checkpoint
        rows = rows[category_start_range::]

        state.total_categories = len(rows)

        state.log(f"reading {state.total_categories} categories from {category_file_input}")

        with Live(render_dashboard(state, progress), refresh_per_second=10) as live:
            categories_task = progress.add_task("Categories", total=state.total_categories)

            for row in rows:

                cat_id = row["id"]
                cat_title = row.get("title_en") or row.get("title_fa", "-")
                state.category_id = cat_id
                state.category_title = cat_title
                state.pages_done = 0
                state.products_done = 0
                state.products_total = 0
                category_pages_start = state.pages_saved
                category_products_start = state.products_saved
                state.log(f"processing category {cat_id} ({cat_title})")
                live.update(render_dashboard(state, progress))

                try:
                    category_page_url = f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products"
                    category_page_json = requests.get(category_page_url).json()
                    logger.info(f"category {cat_id} fetched from {category_page_url}")

                except (requests.exceptions.ProxyError, requests.exceptions.SSLError) as e:
                    logger.error(e)
                    state.errors += 1
                    state.log(f"skipped category {cat_id} due to connection error")
                    live.update(render_dashboard(state, progress))
                    continue

                try:
                    pager = find_all_keys(category_page_json, "pager")[0]

                except (IndexError, KeyError, TypeError):
                    logger.error("invalid response or no pager found")
                    logger.info(f"URL: {category_page_json}")
                    state.errors += 1
                    state.log(f"skipped category {cat_id} (no pager in response)")
                    live.update(render_dashboard(state, progress))
                    continue

                total_items = pager["total_items"]
                total_slots = pager["total_slots"]

                approximate_page_numbers = total_items // 20 + 1

                if approximate_page_numbers > 500:
                    approximate_page_numbers = 500

                state.pages_total = approximate_page_numbers
                state.log(f"category {cat_id}: ~{approximate_page_numbers} pages, {total_slots} slots")
                live.update(render_dashboard(state, progress))

                category_dir = CATEGORY_DIR / cat_id
                page_dir = category_dir / "page"
                product_dir = category_dir / "product"
                category_dir.mkdir(parents=True, exist_ok=True)
                page_dir.mkdir(parents=True, exist_ok=True)
                product_dir.mkdir(parents=True, exist_ok=True)

                pages_task = progress.add_task(
                    f"Pages · {cat_id}",
                    total=approximate_page_numbers,
                )
                products_task: TaskID = progress.add_task(
                    f"Products · {cat_id}",
                    total=1,
                )

                # continue from page checkpoint
                if category_page_checkpoint is not None:
                    page_start_index = int(category_page_checkpoint)

                else:
                    page_start_index = 1

                category_page_checkpoint = 1

                for category_pn in range(page_start_index, approximate_page_numbers + 1):

                    if total_slots == 0:
                        state.log("no more products to fetch")
                        break

                    try:
                        data = requests.get(
                            f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products?page={category_pn}"
                        ).json()

                        logger.info(f"page {category_pn} fetched from https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products?page={category_pn}")
                        
                    except requests.exceptions.RequestException as e:
                        logger.error(e)
                        state.errors += 1
                        state.log(f"error fetching page {category_pn}, skipping")
                        live.update(render_dashboard(state, progress))
                        continue

                    with open(page_dir / f"page_{category_pn}.json", "w", encoding="utf-8") as comments_json_file:
                        json.dump(data, comments_json_file, indent=4, ensure_ascii=False)

                    state.pages_saved += 1
                    state.pages_done += category_pn
                    progress.update(pages_task, advance=1)
                    state.log(f"category {cat_id} page_{category_pn} saved")

                    try:
                        widget = find_all_keys(data, "widgets")[1]
                        items = find_all_keys(widget, "data")
                    except (IndexError, KeyError, TypeError):
                        logger.error("invalid response or data unavailable")
                        logger.info("could not find 'widget' in response")
                        state.errors += 1
                        state.log(f"page {category_pn}: no widget data found, skipping")
                        live.update(render_dashboard(state, progress))
                        continue

                    state.products_total = len(items)
                    state.products_done = 0
                    progress.reset(products_task, total=len(items))
                    live.update(render_dashboard(state, progress))


                    # products storage 
                    for item in items:

                        try:
                            product_id = item["id"]
                        except KeyError:
                            state.skipped += 1
                            logger.info(f"skipping item without id: {item}")
                            continue

                        product_url = f"https://api.digikala.com/v2/product/{product_id}/"

                        try:
                            product = requests.get(product_url).json()
                            logger.debug(f"product {product_id} fetched from {product_url}")
                        except requests.exceptions.RequestException as e:
                            logger.error(e)
                            state.errors += 1
                            state.log(f"product {product_id} failed, skipping")
                            continue

                        current_product_dir = product_dir / f"{product_id}"
                        current_product_dir.mkdir(parents=True, exist_ok=True)
                        current_product_path =  current_product_dir / "details.json"
                        current_comment_path =  current_product_dir / "comments.json"
                        curent_questions_path = current_product_dir / "questions.json"

                        with open(current_product_path, "w", encoding="utf-8") as details_json_file:
                            json.dump(product, details_json_file, indent=4, ensure_ascii=False)



                        # comments storage 
                        comments_page_url = f"https://api.digikala.com/v1/rate-review/products/{product_id}/"
                        comments_page_json = requests.get(comments_page_url).json()
                        try:
                            pager = find_all_keys(comments_page_json, "pager")[0]
                        except (IndexError, KeyError, TypeError):
                            continue
                        total_comments = pager["total_items"]
                        total_pages = pager["total_pages"]
                        all_comments = []
                        for comments_pn in range(1, total_pages + 1):
                            try:
                                data = requests.get(
                                    f"https://api.digikala.com/v1/rate-review/products/{product_id}/?page={comments_pn}"
                                ).json()
                            except requests.exceptions.RequestException as e:
                                continue
                            current_page_comments = find_all_keys(data, "data")
                            all_comments.extend(current_page_comments)
                        with open(current_comment_path, "w", encoding="utf-8") as f:
                            json.dump(all_comments, f, indent=4, ensure_ascii=False)


                        # questions storage 
                        question_page_url = f"https://api.digikala.com/v1/product/{product_id}/carousel-questions/"
                        question_page_json = requests.get(question_page_url).json()
                        try:
                            pager = find_all_keys(question_page_json, "pager")[0]
                        except (IndexError, KeyError, TypeError):
                            continue
                        total_questions = pager["total_items"]
                        total_pages = pager["total_pages"]
                        all_questions = []

                        for question_pn in range(1, total_pages + 1):
                            try:
                                data = requests.get(
                                    f"https://api.digikala.com/v1/product/{product_id}/carousel-questions/?page={question_pn}"
                                ).json()
                            except requests.exceptions.RequestException as e:
                                continue
                            current_page_questinos = find_all_keys(data, "data")
                            all_questions.extend(current_page_questinos)
                        with open(curent_questions_path, "w", encoding="utf-8") as f:
                            json.dump(all_questions, f, indent=4, ensure_ascii=False)

                        state.log(f"product {product_id}: details, comments, questions saved")
                        logger.info(f"product {product_id}: details, comments, questions saved")


                        state.products_saved += 1
                        state.products_done += 1
                        progress.update(products_task, advance=1)
                        live.update(render_dashboard(state, progress))

                    with open(checkpoint_file, "a", newline="") as f:

                        writer = csv.writer(f)
                        writer.writerow([cat_id, category_pn, datetime.now().strftime("%Y/%m/%d, %H:%M:%S")])

                progress.remove_task(pages_task)
                progress.remove_task(products_task)

                state.categories_done += 1
                progress.update(categories_task, advance=1)
                state.log(
                    f"category {cat_id} finished "
                    f"({state.pages_saved - category_pages_start} pages, "
                    f"{state.products_saved - category_products_start} products)"
                )
                live.update(render_dashboard(state, progress))

            progress.update(categories_task, completed=state.total_categories)
            state.log("crawl finished")
            live.update(render_dashboard(state, progress))


if __name__ == "__main__":
    main()
