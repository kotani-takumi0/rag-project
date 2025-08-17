# core/retriever.py
import json, re, pickle, os
from rank_bm25 import BM25Okapi

def j2grams(text: str):
    """日本語向け: 文字2-gramに分割。空白は除去"""
    s = re.sub(r"\s+", "", str(text))
    return [s[i:i+2] for i in range(len(s)-1)] if len(s) > 1 else ([s] if s else [])

def build_bm25(chunks_path="index/chunks.jsonl",
               bm25_path="index/bm25.pkl",
               map_path="index/chunk_map.pkl"):
    os.makedirs(os.path.dirname(bm25_path) or ".", exist_ok=True)
    docs = []
    chunk_map = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            ch = json.loads(line)
            docs.append(j2grams(ch["text"]))
            chunk_map.append({
                "chunk_id": ch["chunk_id"],
                "doc_id": ch["doc_id"],
                "title": ch.get("title"),
                "section": ch.get("section"),
                "url": ch.get("url"),
                "text": ch["text"]
            })
    bm25 = BM25Okapi(docs)
    with open(bm25_path, "wb") as f: pickle.dump(bm25, f)
    with open(map_path, "wb") as f: pickle.dump(chunk_map, f)
    print(f"BM25 built on {len(chunk_map)} chunks")

def search_bm25(query: str, top_k=8,
                bm25_path="index/bm25.pkl",
                map_path="index/chunk_map.pkl"):
    with open(bm25_path, "rb") as f: bm25 = pickle.load(f)
    with open(map_path, "rb") as f: chunk_map = pickle.load(f)
    tokens = j2grams(query)
    scores = bm25.get_scores(tokens)
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    out = []
    for i in idxs:
        ch = chunk_map[i]
        out.append({
            "score": float(scores[i]),
            **ch,
            "snippet": ch["text"][:220]
        })
    return out
