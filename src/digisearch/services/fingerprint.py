import hashlib

from digisearch.services.document import generate_document


def document_and_hash(product: dict) -> tuple[str, str]:
    doc = generate_document(product)
    return doc, hashlib.sha256(doc.encode("utf-8")).hexdigest()