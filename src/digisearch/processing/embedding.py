from pathlib import Path
import json

from FlagEmbedding import BGEM3FlagModel

from digisearch.paths import BGE_EMBEDDINGS_DIR, SEARCH_DOCUMENTS_PRODUCT_DIR, LOG_DIR
import logging


logger = logging.getLogger('ebmedding')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_DIR / 'process.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.info("embedding started")

def get_model(model_name):
    return BGEM3FlagModel(
        model_name,
        use_fp16=True,
    )

model = get_model("BAAI/bge-m3")
logger.info(f"{str(model)}")

def load_documents():
    documents = []

    for path in SEARCH_DOCUMENTS_PRODUCT_DIR.glob("*.txt"):
        product_id = path.stem
        text = path.read_text(encoding="utf-8")

        documents.append({
            "product_id": product_id,
            "text": text,
        })

    return documents


def generate_embeddings(documents):
    texts = [doc["text"] for doc in documents]

    result = model.encode(
        texts,
        batch_size=4,
        max_length=1024,
    )

    return result["dense_vecs"]


def save_embeddings(documents, embeddings):

    for doc, vector in zip(documents, embeddings):
        output = {
            "product_id": doc["product_id"],
            "vector": vector.tolist(),
        }

        output_path = BGE_EMBEDDINGS_DIR / f"{doc['product_id']}.json"
        output_path.write_text(
            json.dumps(output, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )


if __name__ == "__main__":

    documents = load_documents()
    logger.info(f"{len(documents)} documents loaded.")
    embeddings = generate_embeddings(documents)
    logger.info(f"{len(embeddings)} embeddings generated.")

    save_embeddings(documents, embeddings)
    logger.info("embeddings saved.")

