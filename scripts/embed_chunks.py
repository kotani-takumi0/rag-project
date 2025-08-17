import os, json, time
import numpy as np

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from openai._exceptions import APIError, RateLimitError, APIConnectionError
import faiss

MODEL = "text-embedding-3-small"
BATCH_SIZE = 128
INPUT_FILE = "data/processed/policy_chunks.jsonl"
EMB_NPY = "embed/policy_embeddings.npy"
META_JSONL = "embed/policy_metadata.jsonl"
FAISS_INDEX = "embed/policy_faiss.index"

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            try:
                obj = json.loads(line)
                if obj.get("text"):
                    rows.append(obj)
            except json.JSONDecodeError as e:
                print(f"[WARN] line {i} skip: {e}")
    return rows

def batched(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def embed_batch(client, texts, retries=5):
    for a in range(retries):
        try:
            r = client.embeddings.create(model=MODEL, input=texts)
            return [d.embedding for d in r.data]
        except (RateLimitError, APIError, APIConnectionError) as e:
            wait = min(2**a, 30)
            print(f"[WARN] retry in {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError("embedding失敗")

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY が設定されていません")

    client = OpenAI(api_key=api_key)
    rows = read_jsonl(INPUT_FILE)
    if not rows:
        raise SystemExit("text付きの行がありません")

    texts = [r["text"] for r in rows]
    all_vecs = []

    for batch in batched(texts, BATCH_SIZE):
        vecs = embed_batch(client, batch)
        all_vecs.extend(vecs)

    X = np.array(all_vecs, dtype="float32")
    np.save(EMB_NPY, X)

    with open(META_JSONL, "w", encoding="utf-8") as fw:
        for i, r in enumerate(rows):
            out = {"row": i, "id": r.get("id", str(i)), "text": r.get("text",""), "meta": r.get("meta",{})}
            fw.write(json.dumps(out, ensure_ascii=False)+"\n")

    faiss.normalize_L2(X)
    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)
    faiss.write_index(index, FAISS_INDEX)

    print("✅ 完了しました:", X.shape)

if __name__ == "__main__":
    main()