import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

from digisearch.rag.context import *
from digisearch.paths import CANONICAL_PRODUCTS_DIR
from digisearch.rag.context import build_context
from digisearch.qdrant.qdrant_retrieval import search
import re

load_dotenv()

API_KEY = os.environ["CF_API_KEY"]
ACCOUNT_ID = os.environ["CF_ACCOUNT_ID"]
API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/"
headers = {"Authorization": "Bearer {}".format(API_KEY)}


def run(model, inputs):
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()


def get_prompt(query, retrieval_context, history):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": ONE_SHOT_USER},
        {"role": "assistant", "content": ONE_SHOT_ASSISTANT},
        {"role": "user", "content": ONE_SHOT_USER_GREETING},
        {"role": "assistant", "content": ONE_SHOT_ASSISTANT_GREETING},
        {"role": "user", "content": ONE_SHOT_USER_MIXED},
        {"role": "assistant", "content": ONE_SHOT_ASSISTANT_MIXED},
        {"role": "user", "content": ONE_SHOT_USER_BROWSE},
        {"role": "assistant", "content": ONE_SHOT_ASSISTANT_BROWSE},
    ]

    if history:
        messages.extend(history)

    user_content = (
        f"Relevant Products (may be empty or irrelevant if not applicable):\n{retrieval_context}\n\n"
        f"Customer message:\n{query}"
    )

    messages.append({"role": "user", "content": user_content})

    return messages


def get_rag_response(query, top_k, history=None):

    results = search(query, top_k)
    retrieval_context, references = build_context(results)
    messages = get_prompt(query, retrieval_context, history)
    output = run("@cf/qwen/qwen3-30b-a3b-fp8", messages)
    raw_response = output["result"]["response"]
    return resolve_product_links(raw_response, get_url)