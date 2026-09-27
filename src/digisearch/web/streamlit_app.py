import streamlit as st

from digisearch.web.branding import LOGO_PATH, render_header


st.set_page_config(
    page_title="DigiSearch",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
    layout="wide",
)


search_page = st.Page("search_page.py", title="Search",)
ingest_page = st.Page("ingest_page.py", title="Ingest",)
process_page = st.Page("process_page.py", title="Process")
chat_page = st.Page("chat_page.py", title="Chat")
readme_page = st.Page("readme_page.py", title="README")


pg = st.navigation([ingest_page, process_page, search_page, chat_page, readme_page])



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

    /* Chat page styling — bubbles are st.container(key=...) elements, which
       Streamlit marks with a `st-key-<key>` class. We match on a shared
       prefix substring so one rule covers every message of a given role,
       regardless of that message's unique key suffix. */
    [class*="st-key-chat_shell_"] {
        max-width: 900px;
        margin: 0 auto;
    }

    [class*="st-key-bubble_"] {
        max-width: 80%;
        margin: 0 0 16px 0;
        padding: 14px 18px;
        border-radius: 16px;
        line-height: 1.85;
        font-size: 14.5px;
        box-shadow: 0 2px 6px rgba(64, 17, 26, 0.05);
    }

    [class*="st-key-bubble_"],
    [class*="st-key-bubble_"] * {
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    [class*="st-key-bubble_"] p {
        margin: 0 0 8px 0;
    }

    [class*="st-key-bubble_"] p:last-child {
        margin-bottom: 0;
    }

    [class*="st-key-bubble_"] ul,
    [class*="st-key-bubble_"] ol {
        padding-right: 22px;
        padding-left: 0;
        margin: 8px 0;
    }

    [class*="st-key-bubble_"] ol > li {
        margin-bottom: 12px;
    }

    [class*="st-key-bubble_"] li {
        margin-bottom: 5px;
    }

    [class*="st-key-bubble_"] a {
        font-weight: 600;
        text-decoration: none;
        border-bottom: 1px solid currentColor;
    }

    [class*="st-key-bubble_"] code {
        padding: 2px 6px;
        border-radius: 4px;
        direction: ltr !important;
        display: inline-block;
    }

    .chat-role-label {
        font-weight: 700;
        font-size: 12px;
        margin-bottom: 8px;
        opacity: 0.8;
    }

    /* Assistant: left side, light card */
    [class*="st-key-bubble_assistant_"] {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        color: #212529;
        margin-right: auto;
        margin-left: 0;
        border-bottom-left-radius: 4px;
    }
    [class*="st-key-bubble_assistant_"] strong { color: var(--ds-maroon); }
    [class*="st-key-bubble_assistant_"] a { color: var(--ds-crimson); }
    [class*="st-key-bubble_assistant_"] code { background-color: #eef0f2; }
    [class*="st-key-bubble_assistant_"] .chat-role-label { color: var(--ds-crimson); }

    /* User: right side, solid accent */
    [class*="st-key-bubble_user_"] {
        background: var(--ds-maroon);
        color: #fff;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 4px;
    }
    [class*="st-key-bubble_user_"] strong { color: #ffe3ea; }
    [class*="st-key-bubble_user_"] a { color: #ffe3ea; }
    [class*="st-key-bubble_user_"] code { background-color: rgba(255,255,255,0.15); }
    [class*="st-key-bubble_user_"] .chat-role-label { color: #ffe3ea; }

    /* Chat input styling */
    [data-testid="stChatInput"] {
        max-width: 900px;
        margin: 0 auto;
    }

    [data-testid="stChatInput"] > div {
        background-color: white;
        border-radius: 24px;
        border: 1px solid #dee2e6;
    }

    [data-testid="stChatInput"] textarea {
        font-family: 'Vazirmatn', sans-serif;
        font-size: 14px;
        direction: rtl;
        text-align: right;
    }

    /* Sidebar button font styling */
    .stButton > button {
        font-family: 'Vazirmatn', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_header()

pg.run()