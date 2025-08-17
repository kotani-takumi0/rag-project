# scripts/build_bm25.py
# 使い方: python scripts/build_bm25.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.retriever import build_bm25

if __name__ == "__main__":
    build_bm25(
        chunks_path="index/chunks.jsonl",
        bm25_path="index/bm25.pkl",
        map_path="index/chunk_map.pkl",
    )
