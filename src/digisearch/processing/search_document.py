import json
import logging
from digisearch.paths import CANONICAL_DIR, SEARCH_DOCUMENTS_DIR, SEARCH_DOCUMENTS_PRODUCT_DIR, LOG_DIR


logger = logging.getLogger('search_documents')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / 'process.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


_normalizer = None


def get_normalizer():
    """Lazily import/instantiate hazm's Normalizer so importing this module stays cheap."""
    global _normalizer
    if _normalizer is None:
        from hazm import Normalizer
        _normalizer = Normalizer(persian_numbers=False, persian_style=False)
    return _normalizer


def translate():

    fa = {}

    fa["product_categories"] = "دسته‌بندی‌ها"
    fa["product_title_fa"] = "عنوان فارسی"
    fa["product_title_en"] = "عنوان انگلیسی"
    fa["product_specifications"] = "مشخصات محصول"
    fa["product_attributes"] = "ویژ‌گی‌های محصول"

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


def flatten(value):
    fa = translate()
    out = []

    if isinstance(value, list) and len(value) > 1:
        if isinstance(value[0], dict):
            for _value in value:
                for k, v in _value.items():
                    if k in fa:
                        k = fa[k]
                    if k != 'variant_price':
                        if isinstance(v, list):
                            out.extend([f'\n {k}: ', ', '.join(v), ])
                        else:
                            out.extend([f'\n {k}: {v}'])
        else:
            out.extend(value)

    elif isinstance(value, list) and len(value) == 1:
        if isinstance(value[0], dict):
            for _value in value:
                for k, v in _value.items():
                    if k in fa:
                        k = fa[k]
                    if k != 'variant_price':
                        out.extend([f'{k}: {v}'])

    elif isinstance(value, str):
        out.extend([value])

    else:
        out.extend('')

    return '\n'.join(out)


def generate_fa_doc(file_path: str):
    with open(file_path, "r", encoding='utf-8') as file:
        f = file.read()

    fa = translate()
    doc = {}
    context = json.loads(f)

    for k, v in context.items():
        if k in fa:
            doc[fa[k]] = flatten(v)
    return doc


def normalize_fa_doc(document: dict):
    normalizer = get_normalizer()
    text = []
    for k, v in document.items():
        k = normalizer.normalize(k)
        k = normalizer.correct_spacing(k)
        v = normalizer.normalize(v)
        v = normalizer.correct_spacing(v)
        t = f'{k}: {v}'
        text.append(t)
    return text


def search_document_exists(product_id):
    f = SEARCH_DOCUMENTS_DIR / f"{product_id}.txt"
    return f.exists()



def build_search_documents(progress_callback=None) -> dict:

    product_list_path = CANONICAL_DIR / "product_list.json"
    if not product_list_path.exists():
        logger.error(f"{product_list_path} not found. Run the 'List Products' stage first.")
        raise FileNotFoundError(
            f"{product_list_path} not found. Run the 'List Products' stage first."
        )

    with open(product_list_path, "r", encoding="utf-8") as file:
        f = file.read()
    logger.info("product_list.json read.")

    entries = json.loads(f)
    total = len(entries)
    success = 0
    failed = 0

    for i, p in enumerate(entries):
        product_id = None
        try:
            product_id = p['product'].get('id')

            if search_document_exists(product_id):
                continue

            product_canonical_path = CANONICAL_DIR / "products" / f"{product_id}.json"
            doc = generate_fa_doc(str(product_canonical_path))
            text = normalize_fa_doc(doc)

            with open(SEARCH_DOCUMENTS_PRODUCT_DIR / f'{product_id}.txt', 'w', encoding='utf-8') as file:
                file.write('\n\n'.join(text))

            success += 1
            error = None
        except Exception as e:
            failed += 1
            error = str(e)
            logger.warning(f"Failed to build search document for product {product_id}: {e}")

        if progress_callback:
            progress_callback(i + 1, total, product_id, error)

    logger.info(f"{success} documents created at {SEARCH_DOCUMENTS_PRODUCT_DIR} ({failed} failed of {total}).")
    return {"total": total, "success": success, "failed": failed}


if __name__ == "__main__":
    build_search_documents()
