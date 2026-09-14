import time
import random

import streamlit as st
import pandas as pd
import numpy as np
import json

from digisearch.paths import CANONICAL_PRODUCTS_DIR
from digisearch.qdrant.qdrant_retrieval import search
from digisearch.qdrant.qdrant_init import QdrantUnavailableError

# --------------------------------------------------------------------------
# Global styling
# --------------------------------------------------------------------------

LOADING_MESSAGES = [
    "Digging through the shelves...",
    "Chasing down the best matches...",
    "Searching for the best fits...",
    "Unpacking results for you...",
    "Warming up the recommendation engine...",
]


@st.cache_resource
def load_model():
    from digisearch.processing.embedding import get_model
    return get_model() # type: ignore


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
def card(product_id):
    data = get_canonical(product_id)

    if data is None:
        return """
        <div class='product-card'>
            <p><i class="bi bi-exclamation-circle"></i> Product not found!</p>
        </div>
        """

    product_url = data["product_url"]

    if not product_url.startswith(("http://", "https://")):
        product_url = "https://" + product_url.lstrip("/")
    
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


with st.container():
    load_model()
    prompt = st.chat_input("Search Query")
    topk = st.slider("top-k", 1, 20, 10)

    if prompt:
        try:
            with st.spinner(random.choice(LOADING_MESSAGES)):
                start = time.time()
                results = search(prompt, topk)
                elapsed = time.time() - start
        except QdrantUnavailableError as e:
            st.error(str(e))
            st.stop()
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()

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