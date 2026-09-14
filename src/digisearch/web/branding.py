"""Shared branding: logo header, rendered once from the entrypoint so it's
identical on every page instead of being re-implemented per page.
"""
import streamlit as st
from PIL import Image, ImageChops

from digisearch.paths import PROJECT_ROOT

APP_TITLE = "DigiSearch"
LOGO_PATH = PROJECT_ROOT / "images" / "digisearch_transparent.png"


def _autocrop(img: Image.Image) -> Image.Image:
    """Trim background padding around the logo mark, whether that padding
    is transparent (alpha=0) or a flat opaque color (e.g. white).

    getbbox() alone only trims truly transparent pixels: if the PNG's
    background is opaque white rather than transparent despite the
    filename, getbbox() returns the full untouched canvas and nothing
    gets cropped. So we do both: trim transparency first, then trim any
    remaining flat-color border by diffing against the corner pixel.
    """
    img = img.convert("RGBA")

    alpha_bbox = img.getbbox()
    if alpha_bbox:
        img = img.crop(alpha_bbox)

    if img.width == 0 or img.height == 0:
        return img

    bg_color = img.getpixel((0, 0))
    background = Image.new("RGBA", img.size, bg_color)
    diff = ImageChops.difference(img.convert("RGB"), background.convert("RGB"))
    color_bbox = diff.getbbox()
    if color_bbox:
        img = img.crop(color_bbox)

    return img


@st.cache_data(show_spinner=False)
def get_logo_image() -> Image.Image | None:
    """Load the logo, autocropped to its visible content (see _autocrop)."""
    try:
        img = Image.open(LOGO_PATH)
    except (OSError, ValueError):
        return None
    return _autocrop(img)


def render_header():
    """Logo, centered, at the top of every page. Called once from
    streamlit_app.py, before pg.run(), so it's identical everywhere."""
    logo = get_logo_image()
    if logo is None:
        st.title(APP_TITLE)
        return

    # st.image() has no built-in centering option, so it's sandwiched
    # between two equal empty columns -- the standard Streamlit idiom.
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.image(logo, width=480)