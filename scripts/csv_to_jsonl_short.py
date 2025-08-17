import os, json
import pandas as pd

inp  = 'data/raw/1_2_labour_hosp_only.csv'
outp = 'data/processed/kb_light_clean.jsonl'

FIELDS = ["予算事業ID", "事業名", "事業の目的", "現状・課題", "事業の概要", "事業概要URL"]

df = pd.read_csv(inp, encoding="utf-8")

# 欠けてる列は作成
for col in FIELDS:
    if col not in df.columns:
        df[col] = None

seen_budget_ids = set()
base = os.path.splitext(os.path.basename(inp))[0]
counter = 0

# 出力ディレクトリの作成（なければ作る）
os.makedirs(os.path.dirname(outp) or ".", exist_ok=True)

with open(outp, "w", encoding="utf-8") as w:
    for _, row in df.iterrows():
        # 1) 予算事業IDの正規化（数値->文字列、小数点落ち対策、空白除去）
        bud_raw = row.get("予算事業ID")
        bud = "" if pd.isna(bud_raw) else str(bud_raw).strip()

        # 2) 重複スキップ（最初の1件のみ採用）
        if bud and bud in seen_budget_ids:
            continue
        if bud:
            seen_budget_ids.add(bud)

        # 3) idは単純連番（重複スキップ後に加算）
        counter += 1
        rid = f"doc::{base}::{counter:06d}"

        # 4) 出力レコード（id + 他フィールド）
        rec = {"id": rid}
        for k in FIELDS:
            v = row.get(k)
            # 全フィールドを統一的に正規化（NaN→None、文字列はstrip）
            if pd.isna(v):
                rec[k] = None
            else:
                s = str(v)
                rec[k] = s.strip() if isinstance(v, str) or isinstance(v, (int, float)) else v

        w.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"✅ wrote {outp}")
print(f"- kept: {counter}, unique 予算事業ID: {len(seen_budget_ids)}")
