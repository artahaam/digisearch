import streamlit as st

# Define the pages
search_page = st.Page("search_page.py", title="Search",)
ingest_page = st.Page("ingest_page.py", title="Ingest",)
process_page = st.Page("process_page.py", title="Process")

# Set up navigation
pg = st.navigation([ingest_page, process_page, search_page])

# Run the selected page

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

    .category-card {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin: 0 0 16px 0;
        padding: 16px;
        border: 1px solid #ddd;
        border-radius: 14px;
        background: #fff;
        box-shadow: 0 2px 8px rgba(64, 17, 26, 0.06);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        height: 100%;
    }

    .category-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(115, 29, 44, 0.15);
        border-color: var(--ds-pink);
    }

    .category-code {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        color: var(--ds-maroon);
        background: rgba(166, 45, 67, 0.10);
        padding: 2px 8px;
        border-radius: 20px;
        width: fit-content;
        direction: ltr;
    }

    .category-info h2 {
        margin: 6px 0 3px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--ds-darkest);
    }

    .category-title-en {
        margin: 0 0 4px 0;
        font-size: 11px;
        color: #888;
    }

    .category-parent {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        color: var(--ds-crimson);
        margin-top: 2px;
    }
    .category-card {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 8px;
        width: 100%;
        aspect-ratio: 4 / 3;
        margin: 0 0 14px 0;
        padding: 16px;
        border: 1px solid #ddd;
        border-radius: 14px;
        background: #fff;
        box-shadow: 0 2px 8px rgba(64, 17, 26, 0.06);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        overflow: hidden;
        text-align: center;
    }

    .category-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(115, 29, 44, 0.15);
        border-color: var(--ds-pink);
    }

    .category-code {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        color: var(--ds-maroon);
        background: rgba(166, 45, 67, 0.10);
        padding: 3px 10px;
        border-radius: 20px;
        width: fit-content;
        direction: ltr;
    }

    .category-info {
        min-width: 0;
        width: 100%;
    }

    .category-info h2 {
        margin: 6px 0 3px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--ds-darkest);
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    .category-title-en {
        margin: 0;
        font-size: 12px;
        color: #888;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .category-parent {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        color: var(--ds-crimson);
        margin-top: 3px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pg.run()