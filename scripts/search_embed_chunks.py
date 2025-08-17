#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FAISSインデックス検索
- policy_faiss.index, policy_metadata.jsonl をロード
- クエリを埋め込み→Top-K類似文を返す
"""
import os, json, time, argparse
import numpy as np
import faiss

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from openai._exceptions import APIError, RateLimitError, APIConnectionError

MODEL = "text-embedding-3-small"
META_JSONL = "embed/policy_metadata.jsonl"
FAISS_INDEX = "embed/policy_faiss.index"

def read_meta(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f]

def embed_query(client, text, retries=5):
    for a in range(retries):
        try:
            r = client.embeddings.create(model=MODEL, input=text)
            return np.array(r.data[0].embedding, dtype="float32")[None,:]
        except (RateLimitError, APIError, APIConnectionError) as e:
            wait = min(2**a, 30)
            print(f"[WARN] retry in {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError("query埋め込み失敗")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY が設定されていません")

    client = OpenAI(api_key=api_key)
    metas = read_meta(META_JSONL)
    index = faiss.read_index(FAISS_INDEX)

    q = embed_query(client, args.query)
    faiss.normalize_L2(q)
    sims, ids = index.search(q, args.k)

    for rank,(i,s) in enumerate(zip(ids[0], sims[0]),1):
        m = metas[i]
        snippet = m["text"][:100].replace("\n"," ")
        print(f"{rank}. id={m['id']} score={s:.3f} text='{snippet}...'")

if __name__ == "__main__":
    main()
