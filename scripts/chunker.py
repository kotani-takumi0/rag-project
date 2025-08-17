# scripts/chunker.py
# 使い方:
#   python scripts/chunker.py \
#     --in data/processed/kb_light_clean.with_id.jsonl \
#     --out index/chunks.jsonl \
#     --max-chars 500 --overlap 100
import os, json, re, argparse

SECTIONS = ["事業の目的", "現状・課題", "事業の概要"]

def sentence_split_jp(text: str):
    """
    とても簡単な日本語分割: 句点（。！？）の直後で切る。
    長い一文や句点の無い文章はそのまま1つとして返る。
    """
    if not text:
        return []
    # 改行や連続空白を軽く正規化
    s = re.sub(r"[ \t\u3000]+", " ", str(text))
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    parts = re.split(r"(?<=[。！？])\s*", s)
    return [p.strip() for p in parts if p.strip()]

def window_pack(sentences, max_chars=500, overlap=100):
    """
    文単位でできる限り max_chars に詰める。
    パック後のチャンク間は、末尾 overlap 文字ぶんを次チャンクの先頭に重ねる。
    文が極端に長く max_chars を超える場合は、文字スライスで強制分割。
    """
    if not sentences:
        return []
    chunks = []
    buf = ""

    def flush(buf):
        if buf:
            chunks.append(buf)

    for sent in sentences:
        if len(sent) > max_chars:
            # いったん今のバッファを出す
            flush(buf); buf = ""
            # 長文は強制スライス（オーバーラップ付き）
            step = max(1, max_chars - overlap)
            for i in range(0, len(sent), step):
                piece = sent[i:i+max_chars]
                chunks.append(piece)
        else:
            if not buf:
                buf = sent
            elif len(buf) + 1 + len(sent) <= max_chars:
                buf = f"{buf} {sent}"
            else:
                flush(buf)
                # オーバーラップ付与（bufの末尾 overlap 文字）
                tail = buf[-overlap:] if overlap > 0 else ""
                buf = (tail + " " + sent).strip()
                if len(buf) > max_chars:
                    # それでも溢れた場合は強制スライス
                    step = max(1, max_chars - overlap)
                    for i in range(0, len(buf), step):
                        piece = buf[i:i+max_chars]
                        chunks.append(piece)
                    buf = ""
    flush(buf)
    return chunks

def chunk_record(rec, max_chars, overlap):
    """
    1つの事業レコードからチャンク群を生成。
    """
    out = []
    doc_id = rec.get("id")
    title = rec.get("事業名")
    url   = rec.get("事業概要URL")
    budget_id = rec.get("予算事業ID")

    for sec in SECTIONS:
        raw = rec.get(sec)
        if not raw:
            continue
        sentences = sentence_split_jp(raw)
        texts = window_pack(sentences, max_chars=max_chars, overlap=overlap)
        for idx, txt in enumerate(texts):
            chunk_id = f"{doc_id}#{sec}:{idx:04d}"
            out.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "title": title,
                "section": sec,
                "url": url,
                "予算事業ID": budget_id,   # 残したいなら保持
                "text": txt
            })
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    ap.add_argument("--max-chars", type=int, default=500)
    ap.add_argument("--overlap", type=int, default=100)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.outp) or ".", exist_ok=True)

    n_docs = n_chunks = 0
    with open(args.inp, "r", encoding="utf-8") as fin, open(args.outp, "w", encoding="utf-8") as fout:
        for line in fin:
            s = line.strip()
            if not s:
                continue
            rec = json.loads(s)
            chunks = chunk_record(rec, args.max_chars, args.overlap)
            for ch in chunks:
                fout.write(json.dumps(ch, ensure_ascii=False) + "\n")
                n_chunks += 1
            n_docs += 1

    print(f"✅ wrote {args.outp}")
    print(f"- docs: {n_docs}, chunks: {n_chunks}, avg_chunks/doc: {n_chunks/max(1,n_docs):.2f}")

if __name__ == "__main__":
    main()
