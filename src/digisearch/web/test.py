import streamlit as st
import pandas as pd
import numpy as np
import json

from digisearch.paths import PROJECT_ROOT, CANONICAL_PRODUCTS_DIR
from digisearch.qdrant.qdrant_retrieval import search

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
        with open(canonical_path, 'r') as file:
            data = json.loads(file.read())
    except Exception as e:
        print(e)
        data = None
    return data

@st.cache_data
def card(product_id):
    data = get_canonical(product_id)

    if data is None:
        return """Product not found!"""
    
    product_url = data["product_url"]
    product_price = data["product_price"]
    product_image = data["product_images"][0]
    product_title_fa = data["product_title_fa"]
    product_title_en = data["product_title_en"]
    product_brand_fa = data["brand_title_fa"]
    product_brand_en = data["brand_title_en"]

    html = f"""
    <style>
    .product-card {{
        display: flex;
        gap: 12px;
        margin: 8px 0;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: #fff;
        align-items: center;
    }}

    .product-card img {{
        width: 100px;
        height: 100px;
        object-fit: contain;
        border-radius: 6px;
        flex-shrink: 0;
    }}

    .product-info {{
        min-width: 0;
        line-height: 1.3;
    }}

    .product-info h2 {{
        margin: 0 0 3px 0;
        font-size: 15px;
    }}

    .title-en {{
        margin: 0 0 5px 0;
        font-size: 11px;
        color: #777;
    }}

    .brand {{
        display: flex;
        gap: 6px;
        font-size: 11px;
        color: #666;
    }}

    .price {{
        margin: 6px 0;
        font-size: 13px;
        font-weight: bold;
    }}

    .product-link {{
        font-size: 11px;
        text-decoration: none;
    }}
    </style>

    <div class="product-card">
        <a href="{product_url}" target="_blank">
            <img src="{product_image}" alt="{product_title_fa}">
        </a>

        <div class="product-info">
            <h2>{product_title_fa}</h2>
            <p class="title-en">{product_title_en}</p>

            <div class="brand">
                <span>{product_brand_fa}</span>
                <span>({product_brand_en})</span>
            </div>

            <p class="price">{product_price:,} ریال</p>

            <a class="product-link" href="{product_url}" target="_blank">
                مشاهده محصول
            </a>
        </div>
    </div>
    """
    return html


load_model()

st.image(PROJECT_ROOT / "images" / "digisearch.png")


with st.container():
    prompt = st.chat_input("Search Query")
    topk = st.slider('top-k', 1, 20, 10)
    if prompt:
        st.write(f"Results for: {prompt}")

        for res in search(prompt, topk):
            res = res.model_dump()
            product_id = res["id"]
            with st.container():
                st.html(card(product_id))
