import time
import random
import base64

import streamlit as st
import pandas as pd
import numpy as np
import json

from digisearch.paths import PROJECT_ROOT, CANONICAL_PRODUCTS_DIR
from digisearch.qdrant.qdrant_retrieval import search

_LOGO_PATH = PROJECT_ROOT / "images" / "digisearch_transparent.png"

st.set_page_config(
    page_title="DigiSearch",
    page_icon=str(_LOGO_PATH) if _LOGO_PATH.exists() else None,
    layout="wide",
)

# --------------------------------------------------------------------------
# Global styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap');
    @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css');

    :root {
        --ds-white: #FFFFFF;
        --ds-darkest: #731D2C;
        --ds-maroon: #731D2C;
        --ds-crimson: #A62D43;
        --ds-pink: #F24162;
    }

    html, body, [class*="css"]  {
        font-family: 'Vazirmatn', sans-serif;
    }

    .stApp {
        background: var(--ds-white);
    }

    .ds-hero {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }

    .ds-hero img {
        display: block;
        width: 700px;
        height: 400px;
        object-fit: contain;
        border-radius: 12px;
    }

    .ds-stats {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        color: var(--ds-darkest);
        font-size: 13px;
        margin: -6px 0 18px 0;
    }

    .product-card {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: 0 0 16px 0;
        padding: 14px;
        border: 1px solid #ddd;
        border-radius: 14px;
        background: #fff;
        box-shadow: 0 2px 8px rgba(64, 17, 26, 0.06);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        height: 100%;
    }

    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(115, 29, 44, 0.15);
        border-color: var(--ds-pink);
    }

    .product-card img {
        width: 100%;
        height: 160px;
        object-fit: contain;
        border-radius: 10px;
        background: #f6f6f6;
    }

    .product-info {
        min-width: 0;
        line-height: 1.35;
        color: #222;
    }

    .product-info h2 {
        margin: 0 0 3px 0;
        font-size: 15px;
        font-weight: 600;
        color: var(--ds-darkest);
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    .title-en {
        margin: 0 0 6px 0;
        font-size: 11px;
        color: #888;
    }

    .brand {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        color: var(--ds-maroon);
        background: rgba(166, 45, 67, 0.10);
        padding: 2px 8px;
        border-radius: 20px;
        margin-bottom: 6px;
        width: fit-content;
    }

    .price {
        display: flex;
        align-items: center;
        gap: 6px;
        margin: 4px 0;
        font-size: 15px;
        font-weight: 800;
        color: var(--ds-pink);
    }

    .product-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 4px;
        font-size: 12px;
        font-weight: 600;
        text-decoration: none;
        color: white;
        background: var(--ds-maroon);
        padding: 6px 12px;
        border-radius: 20px;
        text-align: center;
        width: fit-content;
        transition: background 0.15s ease;
    }

    .product-link:hover {
        background: var(--ds-pink);
    }

    .ds-empty {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 40px;
        color: var(--ds-maroon);
        font-size: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

LOADING_MESSAGES = [
    "Digging through the shelves...",
    "Chasing down the best matches...",
    "Searching for the best fits...",
    "Unpacking results for you...",
    "Warming up the recommendation engine...",
]


@st.cache_resource
def load_model():
    from digisearch.processing.embedding import model


@st.cache_data
def web_search(query, topk):
    results = search(query, topk)
    return results


@st.cache_data
def get_canonical(product_id):
    canonical_path = CANONICAL_PRODUCTS_DIR / f"{product_id}.json"
    try:
        with open(canonical_path, "r") as file:
            data = json.loads(file.read())
    except Exception as e:
        print(e)
        data = None
    return data


@st.cache_data
def get_logo_b64(path):
    try:
        return base64.b64encode(path.read_bytes()).decode()
    except Exception as e:
        print(e)
        return None


@st.cache_data
def card(product_id):
    data = get_canonical(product_id)

    if data is None:
        return """
        <div class='product-card'>
            <p><i class="bi bi-exclamation-circle"></i> Product not found!</p>
        </div>
        """

    product_url = data["product_url"]
    product_price = data["product_price"]
    product_image = data["product_images"][0]
    product_title_fa = data["product_title_fa"]
    product_title_en = data["product_title_en"]
    product_brand_fa = data["brand_title_fa"]
    product_brand_en = data["brand_title_en"]

    html = f"""
    <div class="product-card">
        <a href="{product_url}" target="_blank">
            <img src="{product_image}" alt="{product_title_fa}">
        </a>

        <div class="product-info">
            <div class="brand">
                <i class="bi bi-tag"></i>
                <span>{product_brand_fa}</span>
                <span>({product_brand_en})</span>
            </div>
            <h2>{product_title_fa}</h2>
            <p class="title-en">{product_title_en}</p>
            <p class="price"><i class="bi bi-cash-coin"></i> {product_price:,} ریال</p>
            <a class="product-link" href="{product_url}" target="_blank">
                مشاهده محصول <i class="bi bi-arrow-left"></i>
            </a>
        </div>
    </div>
    """
    return html


load_model()


logo_b64 = get_logo_b64(_LOGO_PATH)
if logo_b64:
    st.markdown(
        f"""
        <div class="ds-hero">
            <img src="data:image/png;base64,{logo_b64}" alt="DigiSearch logo">
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.container():

    prompt = st.chat_input("Search Query")
    topk = st.slider("top-k", 1, 20, 10)

    if prompt:
        with st.spinner(random.choice(LOADING_MESSAGES)):
            start = time.time()
            results = search(prompt, topk)
            elapsed = time.time() - start

        results = [res.model_dump() for res in results]

        if not results:
            st.markdown(
                f"""
                <div class="ds-empty">
                    <i class="bi bi-emoji-neutral"></i> No results for "<b>{prompt}</b>". Try a different search!
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="ds-stats">
                    <i class="bi bi-search"></i> Found <b>{len(results)}</b> result(s) for "<b>{prompt}</b>" in {elapsed:.2f}s
                </div>
                """,
                unsafe_allow_html=True,
            )

            cols = st.columns(3)
            for i, res in enumerate(results):
                product_id = res["id"]
                with cols[i % 3]:
                    st.html(card(product_id))