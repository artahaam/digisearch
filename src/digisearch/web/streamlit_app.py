import streamlit as st

from digisearch.web.branding import LOGO_PATH, render_header

# set_page_config must be called exactly once, before any other Streamlit
# command, and only in the entrypoint. Calling it again inside individual
# page files (as search_page.py/process_page.py used to) is what caused the
# layout/title/icon to flicker between pages — each page script runs inside
# this same script run via pg.run(), not as a separate process.
st.set_page_config(
    page_title="DigiSearch",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
    layout="wide",
)

# Define the pages
search_page = st.Page("search_page.py", title="Search",)
ingest_page = st.Page("ingest_page.py", title="Ingest",)
process_page = st.Page("process_page.py", title="Process")
chat_page = st.Page("chat_page.py", title="Chat")
readme_page = st.Page("readme_page.py", title="README")


# Set up navigation
pg = st.navigation([ingest_page, process_page, search_page, chat_page, readme_page])

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

    .stat-tile {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 12px 16px;
        border: 1px solid #ddd;
        border-radius: 14px;
        background: #fff;
        box-shadow: 0 2px 8px rgba(64, 17, 26, 0.06);
        text-align: center;
        height: 100%;
    }

    .stat-tile .stat-value {
        font-size: 22px;
        font-weight: 800;
        color: var(--ds-pink);
    }

    .stat-tile .stat-label {
        font-size: 12px;
        color: var(--ds-maroon);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }

    .stat-tile.stat-offline .stat-value {
        color: #aaa;
    }

    .stage-card {
        padding: 14px 16px;
        border: 1px solid #ddd;
        border-left: 4px solid var(--ds-maroon);
        border-radius: 10px;
        background: #fff;
        margin-bottom: 10px;
    }

    .stage-card.stage-done {
        border-left-color: #3aa76d;
    }

    .stage-card.stage-error {
        border-left-color: var(--ds-pink);
    }

    .stage-card h4 {
        margin: 0 0 4px 0;
        font-size: 15px;
        color: var(--ds-darkest);
    }

    .stage-card p {
        margin: 0;
        font-size: 12px;
        color: #666;
    }

    .ds-header {
        width: 100%;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(64, 17, 26, 0.06);
    }

    .ds-header-img {
        display: block;
        width: 100%;
        height: 200px;
        object-fit: cover;
    }

    .ds-header-title {
        display: block;
        padding: 16px 0;
        text-align: center;
        font-size: 22px;
        font-weight: 800;
        color: var(--ds-darkest);
    }

    .rag-answer {
        direction: rtl;
        text-align: right;
        background: #ffffff;
        border: 1px solid #e9e9e9;
        border-radius: 14px;
        padding: 20px 24px;
        margin: 20px 0;
        line-height: 2;
        font-family: IRANYekan, "Vazirmatn", sans-serif;
        color: #252525;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }

    .rag-answer-title {
        font-size: 15px;
        font-weight: 600;
        color: #ea3d56;
        margin-bottom: 10px;
    }

    .rag-answer-content {
        font-size: 15px;
        white-space: pre-wrap;
    }

    .rag-answer-ref {
        display: inline-block;
        background: #fff0f2;
        color: #ea3d56;
        border-radius: 6px;
        padding: 1px 7px;
        font-weight: 600;
        direction: ltr;
    }

        [data-testid="stChatMessage"] {
        direction: rtl;
    }

    /* Hidden marker divs (added right before each message's content)
       let us tell user vs. assistant bubbles apart and flip them. */
    [data-testid="stChatMessage"]:has(.msg-marker-user) {
        flex-direction: row-reverse;
        text-align: right;
    }

    [data-testid="stChatMessage"]:has(.msg-marker-assistant) {
        flex-direction: row;
        text-align: left;
    }

    .msg-marker-user, .msg-marker-assistant {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_header()

pg.run()