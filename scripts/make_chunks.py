# make_chunks.py
import json, uuid
from pathlib import Path

SRC = "data/processed/kb_light_clean.with_id.jsonl"   # あなたが持っている元ファイル
OUT = "data/processed/policy_chunks.jsonl"

def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def main():
    out = []
    for rec in read_jsonl(SRC):
        # 基本情報
        record_id = rec.get("id")
        title = rec.get("事業名")
        purpose = rec.get("事業の目的")
        issues = rec.get("現状・課題")
        summary = rec.get("事業の概要")
        url = rec.get("事業概要URL")
        bureau = rec.get("局") or rec.get("bureau")
        year = rec.get("年度") or rec.get("year")

        # 埋め込み用テキストを組み立て
        body = ""
        if title:   body += f"【事業名】{title}\n"
        if purpose: body += f"【事業の目的】{purpose}\n"
        if issues:  body += f"【現状・課題】{issues}\n"
        if summary: body += f"【事業の概要】{summary}\n"
        body = body.strip()

        if not body:
            continue

        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "record_id": record_id,
            "title": title,
            "url": url,
            "bureau": bureau,
            "year": year,
            "text": body
        }
        out.append(chunk)

    # 保存（1行=1JSON）
    with open(OUT, "w", encoding="utf-8") as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"作成完了: {OUT} （{len(out)}件）")

if __name__ == "__main__":
    main()
