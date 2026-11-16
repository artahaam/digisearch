import hashlib

from digisearch.services.fingerprint import document_and_hash

BASE = {
    "product_title_fa": "گوشی موبایل",
    "product_title_en": "Phone",
    "brand_title_en": "Acme",
    "product_categories": ["Mobile", "Phones"],
    "product_attributes": [{"Color": ["Red"]}],
    "product_description": "A phone.",
}


def test_hash_is_sha256_of_the_document():
    doc, digest = document_and_hash(BASE)
    assert digest == hashlib.sha256(doc.encode("utf-8")).hexdigest()
    assert len(digest) == 64


def test_same_product_gives_same_hash():
    assert document_and_hash(BASE) == document_and_hash(dict(BASE))


def test_hash_changes_when_embedded_text_changes():
    changed = {**BASE, "product_title_en": "Phone Pro"}
    assert document_and_hash(changed)[1] != document_and_hash(BASE)[1]

    changed = {**BASE, "product_description": "A better phone."}
    assert document_and_hash(changed)[1] != document_and_hash(BASE)[1]


def test_hash_ignores_fields_that_are_not_part_of_the_document():
    # price, rating, ids and fetch timestamps must not trigger re-embedding
    noisy = {
        **BASE,
        "product_id": 42,
        "product_price": 123456,
        "product_rating_rate": 4.8,
        "fetched_at": "2026-01-01T00:00:00Z",
    }
    assert document_and_hash(noisy)[1] == document_and_hash(BASE)[1]


def test_hash_ignores_seo_fields_by_default():
    with_seo = {**BASE, "seo_title": "x", "seo_description": "y"}
    assert document_and_hash(with_seo)[1] == document_and_hash(BASE)[1]


def test_hash_does_not_depend_on_dict_key_order():
    reordered = dict(reversed(list(BASE.items())))
    assert document_and_hash(reordered)[1] == document_and_hash(BASE)[1]