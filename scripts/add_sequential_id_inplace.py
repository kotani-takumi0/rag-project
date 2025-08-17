# add_sequential_id_inplace.py
import json, os

inp  = "data/processed/kb_light_clean.jsonl"      # 今のファイル
outp = "data/processed/kb_light_clean.with_id.jsonl"

base = os.path.splitext(os.path.basename(inp))[0]
counter = 0

with open(inp,"r",encoding="utf-8") as fin, open(outp,"w",encoding="utf-8") as fout:
    for line in fin:
        s = line.strip()
        if not s:
            continue
        rec = json.loads(s)
        counter += 1
        rec["id"] = f"doc::{base}::{counter:06d}"
        fout.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"wrote {outp}  rows={counter}")
