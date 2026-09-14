import streamlit as st

from digisearch.paths import PROJECT_ROOT


README_PATH = PROJECT_ROOT / "README.md"

md = ''.join(list(README_PATH.read_text())[110:])

with st.container(width=1500):
    st.markdown(md)
