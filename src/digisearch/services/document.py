import re

_normalizer = None

SEP = '، '

PAIR_FIELDS = {'product_specifications', 'product_attributes'}


SECTION_ORDER = (
    'product_title_fa',
    'product_title_en',
    'brand_title_fa',
    'brand_title_en',
    'product_categories',
    'product_attributes',
    'product_specifications',
    'product_variants',
    'product_description',
    'comments_overview',
    'comments_advantages',
    'comments_disadvantages',
    'questions',
)

SEO_FIELDS = ('seo_title', 'seo_description')
HEADER_FIELDS = ('product_title_fa', 'product_title_en', 'brand_title_fa', 'brand_title_en')

CORE_SECTIONS = HEADER_FIELDS + ('product_categories', 'product_attributes', 'product_specifications')
CORE_MAX_LINE = 120    
CORE_MAX_CHARS = 2000

_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٬', '01234567890123456789.,')

_PIECE_SPLIT = re.compile(r'\s-\s|(?<=[.!?؟])\s')


def get_normalizer():
    global _normalizer
    if _normalizer is None:
        from hazm import Normalizer
        _normalizer = Normalizer(correct_spacing=False, persian_numbers=False, persian_style=False)
    return _normalizer


def translate():
    fa = {}

    fa["product_categories"] = "دسته‌بندی‌ها"
    fa["product_title_fa"] = "عنوان فارسی"
    fa["product_title_en"] = "عنوان انگلیسی"
    fa["product_specifications"] = "مشخصات محصول"
    fa["product_attributes"] = "ویژ‌گی‌های محصول"
    fa["product_description"] = "توضیحات محصول"

    fa["product_variants"] = "انواع"
    fa["variant_title"] = "نوع"
    fa["variant_code"] = "کد رنگ"
    fa["variant_hex_code"] = "کد رنگ هگز"
    fa["variant_nature"] = "رنگ"
    fa["variant_label"] = "برچسب نوع"
    fa["variant_size"] = "اندازه"

    fa["brand_title_fa"] = "برند به فارسی"
    fa["brand_title_en"] = "برند به انگلیسی"

    fa["seo_title"] = "عنوان سئو"
    fa["seo_description"] = "توضیحات سئو"

    fa["comments_overview"] = "خلاصه دیدگاه‌های خریدارها"
    fa["comments_advantages"] = "دیدگاه‌های مثبت"
    fa["comments_disadvantages"] = "دیدگاه‌های منفی"

    fa["questions"] = "پرسش و پاسخ"
    fa["question"] = "پرسش"
    fa["answers"] = "پاسخ‌ها"

    return fa


def _clean(x) -> str:
    if x is None:
        return ''
    s = str(x).replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'(\s*-\s*)+$', '', s) 
    return s.strip()


def _as_list(v) -> list:
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return list(v)
    return [v]


def _flatten_pairs(items, seen: set) -> str:
    if isinstance(items, dict):
        items = [items]

    lines = []
    for item in _as_list(items):
        if not isinstance(item, dict):
            text = _clean(item)
            if text:
                lines.append(text)
            continue

        for name, raw in item.items():
            name = _clean(name)
            values = [_clean(v) for v in _as_list(raw)]
            values = [v for v in values if v]
            if not name or not values:
                continue

            sig = (name, tuple(values))
            if sig in seen:
                continue
            seen.add(sig)

            lines.append(f'{name}: {SEP.join(values)}')

    return '\n'.join(lines)


def _flatten_schema_dicts(items, fa: dict) -> str:
    if isinstance(items, dict):
        items = [items]

    blocks = []
    for item in items:
        if not isinstance(item, dict):
            text = _clean(item)
            if text:
                blocks.append(text)
            continue

        lines = []
        for k, v in item.items():
            if k not in fa or k == 'variant_price':
                continue
            vals = [_clean(x) for x in _as_list(v)]
            vals = [x for x in vals if x]
            if vals:
                lines.append(f'{fa[k]}: {SEP.join(vals)}')
        if lines:
            blocks.append('\n'.join(lines))

    return '\n\n'.join(blocks)


def flatten(value, key: str = None, seen: set = None) -> str:  # type: ignore
    fa = translate()

    if value is None:
        return ''

    if isinstance(value, str):
        return _clean(value)

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, (list, tuple, dict)):
        if key in PAIR_FIELDS:
            return _flatten_pairs(value, seen if seen is not None else set())

        items = [value] if isinstance(value, dict) else list(value)
        if any(isinstance(i, dict) for i in items):
            return _flatten_schema_dicts(items, fa)

        parts = [_clean(i) for i in items]
        return SEP.join(p for p in parts if p)

    return ''


def generate_fa_doc(canonical: dict, include_seo: bool = False) -> dict:
    fa = translate()
    keys = [k for k in SECTION_ORDER if k in canonical]
    keys += [k for k in canonical if k in fa and k not in SECTION_ORDER and k not in SEO_FIELDS]
    if include_seo:
        keys += [k for k in SEO_FIELDS if k in canonical]

    doc = {}
    seen = set()
    for k in keys:
        text = flatten(canonical[k], key=k, seen=seen)
        if text:
            doc[fa[k]] = text
    return doc


def _norm(s: str) -> str:
    normalizer = get_normalizer()
    lines = [normalizer.normalize(line).translate(_DIGITS) for line in s.split('\n')]
    return '\n'.join(lines)


def normalize_fa_doc(document: dict) -> list:
    text = []
    for k, v in document.items():
        k = _norm(k)
        v = _norm(v)
        if '\n' in v:
            text.append(f'{k}:\n{v}')
        else:
            text.append(f'{k}: {v}')
    return text


def generate_document(product: dict, include_seo: bool = False) -> str:
    doc = generate_fa_doc(product, include_seo=include_seo)
    return '\n'.join(normalize_fa_doc(doc)).strip()


# def generate_core_document(product: dict, max_chars: int = CORE_MAX_CHARS) -> str:
#     fa = translate()
#     doc = generate_fa_doc(product)

#     core = {}
#     for k in CORE_SECTIONS:
#         name = fa[k]
#         if name not in doc:
#             continue
#         text = doc[name]
#         if k in PAIR_FIELDS:
#             text = '\n'.join(l for l in text.split('\n') if len(l) <= CORE_MAX_LINE)
#         if text:
#             core[name] = text

#     out = '\n'.join(normalize_fa_doc(core)).strip()
#     if len(out) > max_chars:
#         out = out[:max_chars].rsplit('\n', 1)[0]
#     return out

