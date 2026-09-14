import csv
import time
from collections import deque
from pathlib import Path

import streamlit as st

from digisearch.paths import (
    DATA_DIR,
    RAW_DIR,
    CANONICAL_DIR,
    CANONICAL_PRODUCTS_DIR,
    SEARCH_DOCUMENTS_PRODUCT_DIR,
    BGE_EMBEDDINGS_DIR,
    LOG_DIR,
)
from digisearch.processing import list_products, canonicalize, search_document, embedding
from digisearch.qdrant import qdrant_embedding
from digisearch.qdrant.qdrant_init import get_collection_count, QdrantUnavailableError
from digisearch.categories import fetch_categories_dict
import requests

CATEGORY_DIR = RAW_DIR / "category"
PRODUCT_LIST_PATH = CANONICAL_DIR / "product_list.json"
CHECKPOINT_FILE = DATA_DIR / "checkpoints" / "checkpoint.csv"


# ─────────────────────────────────────────────────────────────────────────
# Dataset overview ("informations")
# ─────────────────────────────────────────────────────────────────────────

def _count_dir_glob(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.glob(pattern))


@st.cache_data(show_spinner=False)
def get_dataset_stats() -> dict:
    raw_categories = _count_dir_glob(CATEGORY_DIR, "*") if CATEGORY_DIR.exists() else 0
    raw_products = sum(1 for _ in RAW_DIR.glob("category/*/product/*")) if RAW_DIR.exists() else 0

    listed_products = 0
    if PRODUCT_LIST_PATH.exists():
        import json
        try:
            listed_products = len(json.loads(PRODUCT_LIST_PATH.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            listed_products = 0

    canonical_products = _count_dir_glob(CANONICAL_PRODUCTS_DIR, "*.json")
    search_documents = _count_dir_glob(SEARCH_DOCUMENTS_PRODUCT_DIR, "*.txt")
    embeddings = _count_dir_glob(BGE_EMBEDDINGS_DIR, "*.json")

    return {
        "raw_categories": raw_categories,
        "raw_products": raw_products,
        "listed_products": listed_products,
        "canonical_products": canonical_products,
        "search_documents": search_documents,
        "embeddings": embeddings,
    }


@st.cache_data(show_spinner=False)
def get_category_titles() -> dict:
    """Map category id -> display title, e.g. 'موبایل (Mobile)'.

    Best-effort: if the Digikala category dictionary can't be fetched
    (offline, API change, timeout), returns an empty dict so the breakdown
    table still renders with '-' in place of titles instead of crashing.
    """
    try:
        categories = fetch_categories_dict()
    except (requests.exceptions.RequestException, IndexError, KeyError, TypeError, ValueError):
        return {}

    titles = {}
    for cat_id, entry in categories.items():
        cat = entry.get("category", {})
        title_fa = cat.get("title_fa")
        title_en = cat.get("title_en")
        if title_fa and title_en:
            titles[str(cat_id)] = f"{title_fa} ({title_en})"
        else:
            titles[str(cat_id)] = title_fa or title_en or "-"
    return titles


@st.cache_data(show_spinner=False)
def get_category_breakdown() -> list[dict]:
    """Per-category crawl detail: products/pages on disk + last checkpointed page and date.

    checkpoint.csv (shared with the crawler) gets one row appended per page
    fetched, so we keep only the last row seen per category to get its most
    recent state.
    """
    if not CATEGORY_DIR.exists():
        return []

    latest_checkpoint: dict[str, dict] = {}
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    cat_id = row.get("cat_id")
                    if cat_id:
                        latest_checkpoint[cat_id] = row  # later rows overwrite earlier ones
        except (OSError, csv.Error) as e:
            st.warning(f"Could not read checkpoint file: {e}")

    titles = get_category_titles()

    rows = []
    for cat_dir in sorted(CATEGORY_DIR.iterdir(), key=lambda p: p.name):
        if not cat_dir.is_dir():
            continue

        product_dir = cat_dir / "product"
        product_count = sum(1 for p in product_dir.iterdir() if p.is_dir()) if product_dir.exists() else 0

        page_dir = cat_dir / "page"
        pages_saved = _count_dir_glob(page_dir, "*.json")

        checkpoint = latest_checkpoint.get(cat_dir.name, {})

        rows.append({
            "Category ID": cat_dir.name,
            "Category Title": titles.get(cat_dir.name, "-"),
            "Products": product_count,
            "Pages saved": pages_saved,
            "Last page checkpointed": checkpoint.get("page", "-"),
            "Last crawled": checkpoint.get("date", "-"),
        })

    return rows


def stat_tile(label: str, value, icon: str, offline: bool = False):
    offline_class = " stat-offline" if offline else ""
    display_value = "offline" if offline else f"{value:,}" if isinstance(value, int) else value
    st.markdown(
        f"""
        <div class="stat-tile{offline_class}">
            <div class="stat-value">{display_value}</div>
            <div class="stat-label"><i class="bi {icon}"></i> {label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tail_file(path: Path, n_lines: int = 200) -> str:
    """Read only the last n_lines of a (potentially large) log file."""
    if not path.exists():
        return "(log file not created yet)"
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = deque(f, maxlen=n_lines)
        return "".join(lines) if lines else "(empty)"
    except OSError as e:
        return f"(could not read log: {e})"


st.title("Process Pipeline")
st.caption(
    "Turn crawled raw data into canonical records, search documents, embeddings, "
    "and a searchable Qdrant index. Data and logs are shared with the `digisearch` CLI."
)

col_refresh, _ = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Refresh stats"):
        get_dataset_stats.clear()
        get_category_breakdown.clear()
        get_category_titles.clear()

stats = get_dataset_stats()
qdrant_count = get_collection_count()

cols = st.columns(7)
with cols[0]:
    stat_tile("Categories crawled", stats["raw_categories"], "bi-tag")
with cols[1]:
    stat_tile("Raw products", stats["raw_products"], "bi-box-seam")
with cols[2]:
    stat_tile("Listed products", stats["listed_products"], "bi-list-check")
with cols[3]:
    stat_tile("Canonical products", stats["canonical_products"], "bi-file-earmark-check")
with cols[4]:
    stat_tile("Search documents", stats["search_documents"], "bi-file-text")
with cols[5]:
    stat_tile("Embeddings", stats["embeddings"], "bi-cpu")
with cols[6]:
    stat_tile("Qdrant points", qdrant_count or 0, "bi-database", offline=qdrant_count is None)

with st.expander(f"📋 Category breakdown ({stats['raw_categories']} categories crawled)"):
    breakdown = get_category_breakdown()

    if not breakdown:
        st.caption("No categories crawled yet — run the Ingest page first.")
    else:
        empty_categories = [row for row in breakdown if row["Products"] == 0]
        if empty_categories:
            st.warning(
                f"{len(empty_categories)} categor{'y has' if len(empty_categories) == 1 else 'ies have'} "
                f"0 products on disk — the crawl may have been interrupted or the category may genuinely "
                f"have no listings."
            )

        search = st.text_input("Filter by category ID or title", key="category_breakdown_search")
        rows = (
            [
                row for row in breakdown
                if search.strip() in row["Category ID"] or search.strip() in row["Category Title"]
            ]
            if search
            else breakdown
        )

        total_products = sum(row["Products"] for row in rows)
        st.caption(f"Showing {len(rows)}/{len(breakdown)} categories · {total_products:,} products total")
        st.dataframe(rows, width="stretch", hide_index=True)

st.divider()


# ─────────────────────────────────────────────────────────────────────────
# Stage runners
# ─────────────────────────────────────────────────────────────────────────

def run_list_products_stage():
    total = max(1, list_products.count_categories())
    bar = st.progress(0, text="Starting...")
    log_box = st.empty()
    events = deque(maxlen=8)

    def on_progress(done, tot, category_id):
        events.appendleft(f"category {category_id} scanned")
        bar.progress(done / max(tot, 1), text=f"Categories scanned: {done}/{tot}")
        log_box.text("\n".join(events))

    try:
        result = list_products.build_product_list(progress_callback=on_progress)
    except Exception as e:
        st.error(f"List Products failed: {e}")
        return False

    bar.progress(1.0, text="Done")
    st.success(f"Listed {result['products']} products across {result['categories']} categories.")
    get_dataset_stats.clear()
    return True


def run_canonicalize_stage():
    bar = st.progress(0, text="Starting...")
    log_box = st.empty()
    events = deque(maxlen=8)

    def on_progress(done, total, product_id, error):
        if error:
            events.appendleft(f"⚠ product {product_id} failed: {error}")
        else:
            events.appendleft(f"product {product_id} canonicalized")
        bar.progress(done / max(total, 1), text=f"Products: {done}/{total}")
        log_box.text("\n".join(events))

    try:
        result = canonicalize.run_canonicalization(progress_callback=on_progress)
    except FileNotFoundError as e:
        st.error(str(e))
        return False
    except Exception as e:
        st.error(f"Canonicalize failed: {e}")
        return False

    bar.progress(1.0, text="Done")
    if result["failed"]:
        st.warning(
            f"Canonicalized {result['success']}/{result['total']} products "
            f"({result['failed']} failed — see process.log for details)."
        )
    else:
        st.success(f"Canonicalized all {result['success']} products.")
    get_dataset_stats.clear()
    return True


def run_search_document_stage():
    bar = st.progress(0, text="Starting...")
    log_box = st.empty()
    events = deque(maxlen=8)

    def on_progress(done, total, product_id, error):
        if error:
            events.appendleft(f"⚠ product {product_id} failed: {error}")
        else:
            events.appendleft(f"product {product_id} document built")
        bar.progress(done / max(total, 1), text=f"Products: {done}/{total}")
        log_box.text("\n".join(events))

    try:
        result = search_document.build_search_documents(progress_callback=on_progress)
    except FileNotFoundError as e:
        st.error(str(e))
        return False
    except Exception as e:
        st.error(f"Building search documents failed: {e}")
        return False

    bar.progress(1.0, text="Done")
    if result["failed"]:
        st.warning(
            f"Built {result['success']}/{result['total']} search documents "
            f"({result['failed']} failed — see process.log for details)."
        )
    else:
        st.success(f"Built all {result['success']} search documents.")
    get_dataset_stats.clear()
    return True


def run_embedding_stage(batch_size: int):
    total = max(1, embedding.count_documents())
    bar = st.progress(0, text="Starting...")
    status_box = st.empty()
    log_box = st.empty()
    events = deque(maxlen=8)

    def on_progress(done, tot, error):
        if error:
            events.appendleft(f"⚠ batch failed: {error}")
        else:
            events.appendleft(f"batch done ({done}/{tot})")
        bar.progress(done / max(tot, 1), text=f"Embedded: {done}/{tot}")
        log_box.text("\n".join(events))

    try:
        with st.spinner("Loading embedding model (first run may take a while)..."):
            embedding.get_model()
        status_box.markdown("Model ready — generating embeddings...")
        result = embedding.run(batch_size=batch_size, progress_callback=on_progress)
    except Exception as e:
        st.error(f"Embedding generation failed: {e}")
        return False

    bar.progress(1.0, text="Done")
    if result["total"] == 0:
        st.warning("No search documents found. Run 'Build Search Documents' first.")
    elif result["failed"]:
        st.warning(
            f"Embedded {result['saved']}/{result['total']} documents "
            f"({result['failed']} failed — see process.log for details)."
        )
    else:
        st.success(f"Generated and saved {result['saved']} embeddings.")
    get_dataset_stats.clear()
    return True


def run_qdrant_upsert_stage(batch_size: int):
    bar = st.progress(0, text="Starting...")
    log_box = st.empty()
    events = deque(maxlen=8)

    def on_progress(done, total, error):
        if error:
            events.appendleft(f"⚠ batch failed: {error}")
        else:
            events.appendleft(f"upserted {done}/{total}")
        bar.progress(done / max(total, 1), text=f"Uploaded: {done}/{total}")
        log_box.text("\n".join(events))

    try:
        result = qdrant_embedding.upsert_embeddings(batch_size=batch_size, progress_callback=on_progress)
    except QdrantUnavailableError as e:
        st.error(str(e))
        return False
    except Exception as e:
        st.error(f"Qdrant upload failed: {e}")
        return False

    bar.progress(1.0, text="Done")
    if result["total"] == 0:
        st.warning("No embeddings found. Run 'Generate Embeddings' first.")
    elif result["skipped"]:
        st.warning(
            f"Uploaded {result['upserted']}/{result['total']} points "
            f"({result['skipped']} skipped — see vecdb.log for details)."
        )
    else:
        st.success(f"Uploaded {result['upserted']} points to Qdrant.")
    return True


STAGES = [
    {
        "key": "list_products",
        "title": "1. List Products",
        "description": "Scan crawled raw data and index every product found.",
        "icon": "bi-list-check",
        "ready": lambda: stats["raw_products"] > 0,
        "ready_hint": "No raw products found yet — run the Ingest page first.",
        "runner": lambda: run_list_products_stage(),
    },
    {
        "key": "canonicalize",
        "title": "2. Canonicalize",
        "description": "Extract structured fields (title, price, brand, variants...) per product.",
        "icon": "bi-file-earmark-check",
        "ready": lambda: PRODUCT_LIST_PATH.exists(),
        "ready_hint": "Run 'List Products' first.",
        "runner": lambda: run_canonicalize_stage(),
    },
    {
        "key": "search_document",
        "title": "3. Build Search Documents",
        "description": "Turn canonical records into normalized Persian search documents.",
        "icon": "bi-file-text",
        "ready": lambda: stats["canonical_products"] > 0,
        "ready_hint": "Run 'Canonicalize' first.",
        "runner": lambda: run_search_document_stage(),
    },
    {
        "key": "embedding",
        "title": "4. Generate Embeddings",
        "description": "Encode search documents into BGE-M3 vectors, in batches.",
        "icon": "bi-cpu",
        "ready": lambda: stats["search_documents"] > 0,
        "ready_hint": "Run 'Build Search Documents' first.",
        "runner": None,  # handled separately (needs batch_size input)
    },
    {
        "key": "qdrant",
        "title": "5. Upload to Qdrant",
        "description": "Upsert embeddings into the shared Qdrant vector index, paged in batches.",
        "icon": "bi-database",
        "ready": lambda: stats["embeddings"] > 0,
        "ready_hint": "Run 'Generate Embeddings' first.",
        "runner": None,  # handled separately (needs batch_size input)
    },
]


st.subheader("Pipeline stages")

for stage in STAGES:
    ready = stage["ready"]()
    status_class = "" if ready else "stage-error"
    st.markdown(
        f"""
        <div class="stage-card {status_class}">
            <h4><i class="bi {stage['icon']}"></i> {stage['title']}</h4>
            <p>{stage['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not ready:
        st.caption(f"⏸ {stage['ready_hint']}")

    if stage["key"] == "embedding":
        col_a, col_b = st.columns([1, 3])
        with col_a:
            batch_size = st.number_input(
                "Batch size", min_value=1, max_value=64, value=embedding.DEFAULT_BATCH_SIZE, key="embed_batch_size"
            )
        with col_b:
            if st.button("Run Generate Embeddings", disabled=not ready, key="run_embedding"):
                run_embedding_stage(batch_size)

    elif stage["key"] == "qdrant":
        col_a, col_b = st.columns([1, 3])
        with col_a:
            upsert_batch_size = st.number_input(
                "Upload batch size", min_value=1, max_value=1000,
                value=qdrant_embedding.DEFAULT_UPSERT_BATCH_SIZE, key="qdrant_batch_size"
            )
        with col_b:
            if st.button("Run Upload to Qdrant", disabled=not ready, key="run_qdrant"):
                run_qdrant_upsert_stage(upsert_batch_size)

    else:
        if st.button(f"Run {stage['title']}", disabled=not ready, key=f"run_{stage['key']}"):
            stage["runner"]()

    st.write("")


st.divider()

if st.button("▶ Run Full Pipeline", type="primary"):
    st.markdown("#### 1. List Products")
    ok = run_list_products_stage()
    if ok:
        st.markdown("#### 2. Canonicalize")
        ok = run_canonicalize_stage()
    if ok:
        st.markdown("#### 3. Build Search Documents")
        ok = run_search_document_stage()
    if ok:
        st.markdown("#### 4. Generate Embeddings")
        ok = run_embedding_stage(embedding.DEFAULT_BATCH_SIZE)
    if ok:
        st.markdown("#### 5. Upload to Qdrant")
        ok = run_qdrant_upsert_stage(qdrant_embedding.DEFAULT_UPSERT_BATCH_SIZE)

    if ok:
        st.success("Full pipeline completed successfully!")
    else:
        st.error("Pipeline stopped early — fix the reported error above and re-run.")


st.divider()

with st.expander("📄 View logs"):
    log_choice = st.selectbox(
        "Log file",
        options=["process.log", "vecdb.log", "crawler.log", "pipeline.log", "search.log"],
    )
    n_lines = st.slider("Lines to show (most recent)", 20, 1000, 200)
    st.text(tail_file(LOG_DIR / log_choice, n_lines))