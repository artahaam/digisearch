from digisearch.paths import SEARCH_DOCUMENTS_PRODUCT_DIR
from qdrant_client.models import ScoredPoint


def get_search_document(product_id):
    try:
        path = SEARCH_DOCUMENTS_PRODUCT_DIR / f"{product_id}.txt"
    except: 
        return ""
    
    return path.read_text()


def build_context(results: list[ScoredPoint]):
    contexts = []

    for i, product in enumerate(results):
        payload = product.payload
        print()
        print(payload)
        print()
        
        product_id = product.id
        search_doc = get_search_document(product_id).strip()
        code = i
        context = f"[{code}] {search_doc}"
        contexts.append(context)

    seperator = "-"*10
    return seperator.join(contexts)



