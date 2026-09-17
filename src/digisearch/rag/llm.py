import os
from dotenv import load_dotenv
from openai import OpenAI

from digisearch.rag.context import build_context
from digisearch.qdrant.qdrant_retrieval import search

load_dotenv()

MODEL = "gpt-5.6-luna"

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
)



def get_rag_response(query, top_k):
    results = search(query, top_k)

    print(results[0].id)

    context = build_context(results)

    prompt = f"""
    You are DigiSearch, a product search assistant.

    Use ONLY the product information provided below.
    Do not invent products, features, prices, or specifications.

    PRODUCTS:
    {context}

    USER QUERY:
    {query}

    Answer in Persian.
    If you mention a product, refer to it using its [number] for example:
    [1]
    عنوان: کلاه بافتنی مشکی
    برند: -
    رنگ: مشکی
    جنس: پشم
    مناسب برای: زمستان
    قیمت: 600000 تومان
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


print(get_rag_response("کلاه نارنجی نخی مناسب تابستون برای کوهنوردی", 2))

