from digisearch.services.document import (
    SEP,
    _clean,
    flatten,
    generate_document,
    generate_fa_doc,
    translate,
)

FA = translate()

# --------------------------------------------------------------------------
# _clean
# --------------------------------------------------------------------------


def test_clean_handles_none_and_numbers():
    assert _clean(None) == ""
    assert _clean(5) == "5"


def test_clean_collapses_whitespace_and_nbsp():
    assert _clean("  a \xa0  b  ") == "a b"


def test_clean_strips_trailing_dashes():
    assert _clean("title - ") == "title"
    assert _clean("a - - ") == "a"
    assert _clean("well-known") == "well-known"  # inner dash is kept


# --------------------------------------------------------------------------
# flatten
# --------------------------------------------------------------------------


def test_flatten_scalars():
    assert flatten(None) == ""
    assert flatten("  x  ") == "x"
    assert flatten(3) == "3"
    assert flatten(2.5) == "2.5"
    assert flatten(object()) == ""


def test_flatten_plain_list_joins_with_separator_and_skips_empty():
    assert flatten(["a", " b ", "", None]) == f"a{SEP}b"
    assert flatten([]) == ""


def test_flatten_pair_fields_render_name_and_values():
    value = [{"Color": ["Red", "Blue"]}]
    assert flatten(value, key="product_attributes") == f"Color: Red{SEP}Blue"


def test_flatten_pair_fields_are_deduplicated_through_seen():
    seen = set()
    value = [{"Color": ["Red"]}]
    assert flatten(value, key="product_attributes", seen=seen) == "Color: Red"
    # same pair again (e.g. also present in specifications) is dropped
    assert flatten(value, key="product_specifications", seen=seen) == ""


def test_flatten_variant_dicts_use_translated_labels_and_skip_price_and_unknown():
    value = [{"variant_title": "Red", "variant_price": 5, "unknown": "x"}]
    assert flatten(value, key="product_variants") == f"{FA['variant_title']}: Red"


# --------------------------------------------------------------------------
# generate_fa_doc
# --------------------------------------------------------------------------

CANONICAL = {
    "product_title_fa": "گوشی",
    "product_title_en": "Phone",
    "brand_title_fa": "برند",
    "product_categories": [None, "الف", "ب", None],
    "seo_title": "SEO",
    "product_id": 1,
    "product_price": 999,
}


def test_fa_doc_follows_section_order_and_ignores_unknown_fields():
    doc = generate_fa_doc(CANONICAL)
    assert list(doc) == [
        FA["product_title_fa"],
        FA["product_title_en"],
        FA["brand_title_fa"],
        FA["product_categories"],
    ]
    assert doc[FA["product_categories"]] == f"الف{SEP}ب"


def test_fa_doc_seo_only_when_requested():
    assert FA["seo_title"] not in generate_fa_doc(CANONICAL)
    assert generate_fa_doc(CANONICAL, include_seo=True)[FA["seo_title"]] == "SEO"


def test_fa_doc_drops_empty_sections():
    assert generate_fa_doc({"product_title_fa": "   ", "product_description": None}) == {}


def test_fa_doc_key_order_of_input_does_not_matter():
    reordered = dict(reversed(list(CANONICAL.items())))
    assert list(generate_fa_doc(reordered)) == list(generate_fa_doc(CANONICAL))


# --------------------------------------------------------------------------
# generate_document (uses the hazm normalizer)
# --------------------------------------------------------------------------


def test_generate_document_contains_values():
    doc = generate_document({"product_title_en": "Phone", "brand_title_en": "Acme"})
    assert "Phone" in doc
    assert "Acme" in doc


def test_generate_document_converts_persian_digits_to_ascii():
    doc = generate_document({"product_description": "وزن ۲۰۰ گرم"})
    assert "200" in doc
    assert "۲" not in doc


def test_generate_document_empty_product_is_empty_string():
    assert generate_document({}) == ""