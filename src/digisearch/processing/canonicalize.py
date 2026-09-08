import json
from digisearch.paths import CANONICAL_DIR, CANONICAL_PRODUCTS_DIR, PROJECT_ROOT, LOG_DIR
import logging


logger = logging.getLogger('canonicalize')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_DIR / 'process.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.info("Canonicalization started")



def extract_questions_data(file_path: str):
    with open(file_path, "r", encoding='utf-8') as file:
        f = file.read()
    questions = []
    try:
        loads = json.loads(f)[:5]
        for l in loads:
            _questions = l.get("questions")
            for _question in _questions:

                question = _question.get("text")
                answers = []

                for ans in _question["answers"]:
                    answers.append(ans["text"])

                questions.append({'question': question,
                                    'answers': answers})
    except:
        pass

    questions = {
        'questions':questions
    }
    return questions



def extract_details_data(file_path: str):
    with open(file_path, "r", encoding='utf-8') as file:
        f = file.read()

    f = json.loads(f)
    data = f.get("data", {})

    product = data.get("product", {})
    product_id = product.get("id")
    product_title_fa = product.get("title_fa")
    product_title_en = product.get("title_en")
    product_uri = product.get("url").get("uri")
    product_url = "www.digikala.com" + product_uri
    product_test_title_fa = product.get("test_title_fa")
    product_test_title_en = product.get("test_title_en")

    product_images = []
    try:
        product_images = data.get("seo").get("markup_schema")[0].get("image")
    except:
        pass


    try:
        product_rating_rate = product.get("rating").get("rate")
        product_rating_count = product.get("rating").get("count")
    except:
        product_rating_rate, product_rating_count = 0, 0


    try:
        product_price = product.get("default_variant", {}).get("price", {}).get("selling_price")
    except Exception as e:
        product_price = 0
        pass
    

    product_variants = []
    try:
        variants = product.get("variants", {})
        for v in variants:
            themes = v.get("themes", {})
            variant_title = themes[0].get("value", {}).get("title")
            variant_code = themes[0].get("value", {}).get("code")
            variant_hex_code = themes[0].get("value", {}).get("hex_code")
            variant_nature = themes[0].get("value", {}).get("nature")
            variant_label = themes[0].get("label", {})
            variant_size = v.get("size", {}).get("title")
            variant_price = v.get("price", {}).get("selling_price")
            var = {
                "variant_title": variant_title,
                "variant_code": variant_code,
                "variant_hex_code": variant_hex_code,
                "variant_nature": variant_nature,
                "variant_label": variant_label,
                "variant_size": variant_size,
                "variant_price": variant_price,
            }
            product_variants.append(var)
    except:
        pass

    product_description = ""
    try:
        product_description = product.get("review", {}).get("description")
    except:
        pass
    
    product_attributes = []
    try:
        attributes = product.get("review", {}).get("attributes")
        for attr in attributes:
            title = attr.get("title")
            values = attr.get("values")
            attribute = {title:values}
            product_attributes.append(attribute)
    except:
        pass

    product_specifications = []
    try:
        specifications = product.get("specifications")
        for spec in specifications:
            title = spec.get("title")
            attributes = spec.get("attributes")
            for attr in attributes:
                title = attr.get("title")
                values = attr.get("values")
                attribute = {title:values}
                product_specifications.append(attribute)
    except:
        pass
    



    data_layer = product.get("data_layer", {})
    product_categories = []
    item_category2 = data_layer.get("item_category2")
    item_category3 = data_layer.get("item_category3")
    item_category4 = data_layer.get("item_category4")
    item_category5 = data_layer.get("item_category5")
    product_categories.extend([item_category2, item_category3, item_category4, item_category5])
    product_category = data_layer.get("category")

    brand = product.get("brand", {})
    brand_code = brand.get("code")
    brand_title_fa = brand.get("title_fa")
    brand_title_en = brand.get("title_en")
    _brand_url = brand.get("url", {})
    brand_uri = _brand_url.get("uri", {})
    brand_url = "www.digikala.com" + brand_uri

    try:
        brand_logo_url = brand.get("logo", {}).get("url")
    except AttributeError:
        brand_logo_url = ""


    seo = data.get("seo", {})
    seo_title = seo.get("title")
    seo_description = seo.get("description")


    _comments_overview = product.get("comments_overview", {})
    if not _comments_overview:
        _comments_overview = {}
    comments_overview = _comments_overview.get("overview")
    comments_advantages = _comments_overview.get("advantages")
    comments_disadvantages = _comments_overview.get("disadvantages")




    details = {
        'product_id' : product_id,
        'product_url': product_url,
        'product_price': product_price,
        'product_category': product_category,
        'product_categories': product_categories,
        'product_rating_rate': product_rating_rate,
        'product_rating_count': product_rating_count,
        'product_title_fa': product_title_fa,
        'product_title_en': product_title_en,
        'product_test_title_fa':product_test_title_fa,
        'product_test_title_en':product_test_title_en,
        'product_description': product_description,
        'product_attributes': product_attributes,
        'product_specifications': product_specifications,
        'product_variants': product_variants,
        'product_images': product_images,

        'brand_code': brand_code,
        'brand_title_fa': brand_title_fa,
        'brand_title_en': brand_title_en,
        'brand_url': brand_url,
        'brand_logo_url': brand_logo_url,

        'seo_title': seo_title,
        'seo_description': seo_description,

        'comments_overview': comments_overview,
        'comments_advantages': comments_advantages,
        'comments_disadvantages': comments_disadvantages,
    }

    return details


def extract_comments_data(file_path: str):
    pass


with open(CANONICAL_DIR / "product_list.json", "r") as file:
    f = file.read()



for p in json.loads(f):

    try:
        product_id = p['product'].get('id')
        questions_path = p['product'].get('questions_path')
        details_path = p['product'].get('details_path')
        comments_path = p['product'].get('comments_path')
        category = p['product'].get('category')



        details = extract_details_data(details_path)
        questions = extract_questions_data(questions_path)

        details.update(questions.items())

        
        with open(CANONICAL_PRODUCTS_DIR / f'{product_id}.json', 'w', encoding='utf-8') as file:

            file.write(json.dumps(details, indent=4, ensure_ascii=False))
    except:
        continue
    
logger.info(f"Canonicalization finished.")


