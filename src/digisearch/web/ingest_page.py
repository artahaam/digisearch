import streamlit as st
import requests
import json
import csv
import time
import logging
from pathlib import Path
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field

from digisearch.paths import PROJECT_ROOT, DATA_DIR, RAW_DIR, LOG_DIR
from digisearch.categories import fetch_categories_dict

# ─────────────────────────────────────────────────────────────────────────
# Shared helpers (from crawl.py)
# ─────────────────────────────────────────────────────────────────────────

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


CATEGORY_DIR = RAW_DIR / "category"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
for directory in (CATEGORY_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("crawler")
if not logger.handlers:  # avoid duplicate handlers across Streamlit reruns
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(LOG_DIR / "crawler.log")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

CHECKPOINT_FILE = CHECKPOINT_DIR / "checkpoint.csv"
if not CHECKPOINT_FILE.exists():
    with open(CHECKPOINT_FILE, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(["cat_id", "page", "date"])


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
    events: deque = field(default_factory=lambda: deque(maxlen=8))

    @property
    def elapsed(self) -> str:
        return f"{time.monotonic() - self.started_at:.0f}s"

    def log(self, message: str) -> None:
        self.events.appendleft(f"[{self.elapsed}] {message}")
        logger.info(message)


# ─────────────────────────────────────────────────────────────────────────
# Category dictionary (from ingest_page.py)
# ─────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_cagtegories():
    return fetch_categories_dict()


# ─────────────────────────────────────────────────────────────────────────
# Crawl logic (adapted from crawl.py's main loop, minus argparse/rich)
# ─────────────────────────────────────────────────────────────────────────

def crawl_one_category(cat_id: str, cat_title: str, state: CrawlerState,
                        page_bar, product_bar, status_box, log_box,
                        max_pages: int = 500):
    """Crawl a single category: pages -> products -> comments -> questions."""
    state.category_id = cat_id
    state.category_title = cat_title
    state.pages_done = 0
    state.products_done = 0
    state.products_total = 0
    state.log(f"processing category {cat_id} ({cat_title})")
    status_box.markdown(f"**Category:** {cat_title} (`{cat_id}`)")

    try:
        category_page_url = f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products"
        category_page_json = requests.get(category_page_url, timeout=20).json()
    except requests.exceptions.RequestException as e:
        state.errors += 1
        state.log(f"skipped category {cat_id} due to connection error: {e}")
        return

    try:
        pager = find_all_keys(category_page_json, "pager")[0]
    except (IndexError, KeyError, TypeError):
        state.errors += 1
        state.log(f"skipped category {cat_id} (no pager in response)")
        return

    total_items = pager["total_items"]
    total_slots = pager["total_slots"]

    approximate_page_numbers = total_items // 20 + 1
    if approximate_page_numbers > max_pages:
        approximate_page_numbers = max_pages

    state.pages_total = approximate_page_numbers
    state.log(f"category {cat_id}: ~{approximate_page_numbers} pages, {total_slots} slots")

    category_dir = CATEGORY_DIR / f"{cat_id}"
    page_dir = category_dir / "page"
    product_dir = category_dir / "product"
    for d in (category_dir, page_dir, product_dir):
        d.mkdir(parents=True, exist_ok=True)

    if total_slots == 0:
        state.log(f"category {cat_id}: no products to fetch")
        page_bar.progress(1.0, text="No products in this category")
        return

    for category_pn in range(1, approximate_page_numbers + 1):
        try:
            data = requests.get(
                f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products?page={category_pn}",
                timeout=20,
            ).json()
        except requests.exceptions.RequestException as e:
            state.errors += 1
            state.log(f"error fetching page {category_pn}, skipping: {e}")
            continue

        with open(page_dir / f"page_{category_pn}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        state.pages_saved += 1
        state.pages_done += 1
        page_bar.progress(
            state.pages_done / approximate_page_numbers,
            text=f"Pages: {state.pages_done}/{approximate_page_numbers}",
        )
        state.log(f"category {cat_id} page_{category_pn} saved")
        log_box.text("\n".join(state.events))

        try:
            widget = find_all_keys(data, "widgets")[1]
            items = find_all_keys(widget, "data")
        except (IndexError, KeyError, TypeError):
            state.errors += 1
            state.log(f"page {category_pn}: no widget data found, skipping")
            continue

        state.products_total = len(items)
        state.products_done = 0

        for item in items:
            try:
                product_id = item["id"]
            except KeyError:
                state.skipped += 1
                continue

            product_url = f"https://api.digikala.com/v2/product/{product_id}/"
            try:
                product = requests.get(product_url, timeout=20).json()
            except requests.exceptions.RequestException as e:
                state.errors += 1
                state.log(f"product {product_id} failed, skipping: {e}")
                continue

            current_product_dir = product_dir / f"{product_id}"
            current_product_dir.mkdir(parents=True, exist_ok=True)
            current_product_path = current_product_dir / "details.json"
            current_comment_path = current_product_dir / "comments.json"
            current_questions_path = current_product_dir / "questions.json"

            with open(current_product_path, "w", encoding="utf-8") as f:
                json.dump(product, f, indent=4, ensure_ascii=False)

            # comments
            try:
                comments_page_json = requests.get(
                    f"https://api.digikala.com/v1/rate-review/products/{product_id}/", timeout=20
                ).json()
                pager = find_all_keys(comments_page_json, "pager")[0]
                total_pages = pager["total_pages"]
                all_comments = []
                for comments_pn in range(1, total_pages + 1):
                    data = requests.get(
                        f"https://api.digikala.com/v1/rate-review/products/{product_id}/?page={comments_pn}",
                        timeout=20,
                    ).json()
                    all_comments.extend(find_all_keys(data, "data"))
                with open(current_comment_path, "w", encoding="utf-8") as f:
                    json.dump(all_comments, f, indent=4, ensure_ascii=False)
            except (IndexError, KeyError, TypeError, requests.exceptions.RequestException):
                pass

            # questions
            try:
                question_page_json = requests.get(
                    f"https://api.digikala.com/v1/product/{product_id}/carousel-questions/", timeout=20
                ).json()
                pager = find_all_keys(question_page_json, "pager")[0]
                total_pages = pager["total_pages"]
                all_questions = []
                for question_pn in range(1, total_pages + 1):
                    data = requests.get(
                        f"https://api.digikala.com/v1/product/{product_id}/carousel-questions/?page={question_pn}",
                        timeout=20,
                    ).json()
                    all_questions.extend(find_all_keys(data, "data"))
                with open(current_questions_path, "w", encoding="utf-8") as f:
                    json.dump(all_questions, f, indent=4, ensure_ascii=False)
            except (IndexError, KeyError, TypeError, requests.exceptions.RequestException):
                pass

            state.products_saved += 1
            state.products_done += 1
            product_bar.progress(
                state.products_done / max(state.products_total, 1),
                text=f"Products (page {category_pn}): {state.products_done}/{state.products_total}",
            )
            state.log(f"product {product_id}: details, comments, questions saved")
            log_box.text("\n".join(state.events))

        with open(CHECKPOINT_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([cat_id, category_pn, datetime.now().strftime("%Y/%m/%d, %H:%M:%S")])

    state.categories_done += 1
    state.log(f"category {cat_id} finished")


def run_crawl(selected_ids, id_to_title):
    state = CrawlerState(total_categories=len(selected_ids))

    overall_bar = st.progress(0, text="Starting crawl...")
    status_box = st.empty()
    page_bar = st.progress(0, text="Pages")
    product_bar = st.progress(0, text="Products")
    log_box = st.empty()
    summary_box = st.empty()

    for i, cat_id in enumerate(selected_ids):
        cat_title = id_to_title.get(cat_id, cat_id)
        page_bar.progress(0, text="Pages")
        product_bar.progress(0, text="Products")
        crawl_one_category(cat_id, cat_title, state, page_bar, product_bar, status_box, log_box)
        overall_bar.progress(
            (i + 1) / len(selected_ids),
            text=f"Categories: {i + 1}/{len(selected_ids)}",
        )
        summary_box.caption(
            f"Pages saved: {state.pages_saved} · Products saved: {state.products_saved} · "
            f"Errors: {state.errors} · Skipped: {state.skipped} · Elapsed: {state.elapsed}"
        )

    st.success(f"Crawl finished — {state.categories_done} categories, "
               f"{state.pages_saved} pages, {state.products_saved} products saved.")


# ─────────────────────────────────────────────────────────────────────────
# Page UI
# ─────────────────────────────────────────────────────────────────────────

categories = get_cagtegories()

if "selected_categories" not in st.session_state:
    st.session_state.selected_categories = set()

id_to_label = {}
id_to_title = {}
for cat_id, entry in categories.items():
    cat = entry["category"]
    id_to_label[cat_id] = f"{cat['title_fa']} ({cat['title_en']}) [{cat['code']}]"
    id_to_title[cat_id] = cat["title_en"] or cat["title_fa"]

label_to_id = {v: k for k, v in id_to_label.items()}

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        font-size: 18px;
        min-height: 60px;
    }
    div[data-baseweb="select"] > div {
        min-height: 60px;
        font-size: 18px;
    }
    div[data-baseweb="tag"] {
        font-size: 16px;
        padding: 6px 10px;
        height: auto;
    }
    div[data-baseweb="popover"] {
        min-width: 500px;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] {
        max-height: 500px !important;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] li,
    div[data-baseweb="popover"] li {
        font-size: 16px;
        padding: 10px 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

selected_labels = st.multiselect(
    "Select categories",
    options=list(id_to_label.values()),
    default=[id_to_label[i] for i in st.session_state.selected_categories if i in id_to_label],
)
st.session_state.selected_categories = {label_to_id[l] for l in selected_labels}

st.caption(f"{len(categories)} categories · {len(st.session_state.selected_categories)} selected")

st.divider()

start_disabled = len(st.session_state.selected_categories) == 0
if st.button("Start Crawling", type="primary", disabled=start_disabled):
    run_crawl(list(st.session_state.selected_categories), id_to_title)

if start_disabled:
    st.caption("Select at least one category above to enable crawling.")