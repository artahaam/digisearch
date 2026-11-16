from digisearch.services.canonicalize import (
    extract_details_data,
    extract_questions_data,
)

# --------------------------------------------------------------------------
# extract_questions_data
# --------------------------------------------------------------------------


def test_questions_none_or_empty_gives_empty_list():
    assert extract_questions_data(None) == {"questions": []}
    assert extract_questions_data([]) == {"questions": []}


def test_questions_keep_text_and_answer_texts():
    raw = [{"text": "Is it waterproof?", "answers": [{"text": "Yes"}, {"text": "IP68"}]}]
    assert extract_questions_data(raw) == {
        "questions": [{"question": "Is it waterproof?", "answers": ["Yes", "IP68"]}]
    }


def test_questions_default_limit_is_five():
    raw = [{"text": f"q{i}", "answers": []} for i in range(8)]
    out = extract_questions_data(raw)["questions"]
    assert [q["question"] for q in out] == ["q0", "q1", "q2", "q3", "q4"]


def test_questions_limit_none_returns_everything():
    raw = [{"text": f"q{i}"} for i in range(8)]
    assert len(extract_questions_data(raw, limit=None)["questions"]) == 8


def test_questions_without_text_are_dropped():
    raw = [{"text": "", "answers": [{"text": "x"}]}, {"answers": []}, {"text": "ok"}]
    assert extract_questions_data(raw) == {"questions": [{"question": "ok", "answers": []}]}


def test_answers_without_text_are_dropped():
    raw = [{"text": "q", "answers": [{"text": "a"}, {"text": ""}, {}, {"text": None}]}]
    assert extract_questions_data(raw)["questions"][0]["answers"] == ["a"]


def test_answers_none_is_treated_as_empty():
    raw = [{"text": "q", "answers": None}]
    assert extract_questions_data(raw)["questions"][0]["answers"] == []


def test_limit_is_applied_before_filtering():
    # Documents CURRENT behaviour: the slice happens before empty questions are
    # dropped, so one empty question inside the limit "uses up" a slot.
    raw = [{"text": None}, {"text": "kept"}]
    assert extract_questions_data(raw, limit=1) == {"questions": []}


# --------------------------------------------------------------------------
# extract_details_data
# --------------------------------------------------------------------------

FULL_PAYLOAD = {
    "data": {
        "product": {
            "id": 123,
            "title_fa": "گوشی",
            "title_en": "Phone",
            "test_title_fa": "تست",
            "test_title_en": "Test",
            "url": {"uri": "/product/dkp-123/"},
            "rating": {"rate": 4.5, "count": 10},
            "default_variant": {"price": {"selling_price": 1000}},
            "brand": {
                "code": "b1",
                "title_fa": "برند",
                "title_en": "Brand",
                "url": {"uri": "/brand/b1/"},
                "logo": {"url": "http://logo"},
            },
            "data_layer": {"category": "mobile", "item_category2": "a", "item_category3": "b"},
            "review": {
                "description": "desc",
                "attributes": [{"title": "Color", "values": ["Red"]}],
            },
            "specifications": [
                {"title": "Group", "attributes": [{"title": "Weight", "values": ["200 g"]}]}
            ],
            "variants": [
                {
                    "themes": [
                        {
                            "label": "Color",
                            "value": {
                                "title": "Red",
                                "code": "r",
                                "hex_code": "#f00",
                                "nature": "color",
                            },
                        }
                    ],
                    "size": {"title": "L"},
                    "price": {"selling_price": 900},
                }
            ],
            "comments_overview": {"overview": "ok", "advantages": ["x"], "disadvantages": ["y"]},
        },
        "seo": {"title": "t", "description": "d", "markup_schema": [{"image": ["i1"]}]},
    }
}


def test_details_full_payload():
    d = extract_details_data(FULL_PAYLOAD)

    assert d["product_id"] == 123
    assert d["product_url"] == "www.digikala.com/product/dkp-123/"
    assert d["product_price"] == 1000
    assert d["product_category"] == "mobile"
    assert d["product_categories"] == ["a", "b", None, None]
    assert (d["product_rating_rate"], d["product_rating_count"]) == (4.5, 10)
    assert d["product_title_fa"] == "گوشی"
    assert d["product_description"] == "desc"
    assert d["product_attributes"] == [{"Color": ["Red"]}]
    assert d["product_specifications"] == [{"Weight": ["200 g"]}]
    assert d["product_images"] == ["i1"]
    assert d["product_variants"] == [
        {
            "variant_title": "Red",
            "variant_code": "r",
            "variant_hex_code": "#f00",
            "variant_nature": "color",
            "variant_label": "Color",
            "variant_size": "L",
            "variant_price": 900,
        }
    ]
    assert d["brand_url"] == "www.digikala.com/brand/b1/"
    assert d["brand_logo_url"] == "http://logo"
    assert d["seo_title"] == "t"
    assert d["comments_advantages"] == ["x"]
    assert d["comments_disadvantages"] == ["y"]


def test_details_empty_payload_does_not_raise_and_uses_safe_defaults():
    d = extract_details_data({})

    assert d["product_id"] is None
    assert d["product_url"] == "www.digikala.com"
    assert d["product_rating_rate"] == 0
    assert d["product_rating_count"] == 0
    assert d["product_variants"] == []
    assert d["product_attributes"] == []
    assert d["product_specifications"] == []
    assert d["product_images"] == []
    assert d["product_categories"] == [None, None, None, None]
    assert d["comments_overview"] is None


def test_details_tolerates_null_sections():
    payload = {
        "data": {
            "product": {
                "url": None,
                "rating": None,
                "default_variant": None,
                "review": None,
                "brand": {"url": None, "logo": None},
                "comments_overview": None,
            }
        }
    }
    d = extract_details_data(payload)

    assert d["product_url"] == "www.digikala.com"
    assert d["product_rating_rate"] == 0
    assert d["product_price"] == 0
    assert d["brand_url"] == "www.digikala.com"
    assert d["brand_logo_url"] == ""
    assert d["comments_overview"] is None