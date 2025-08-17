# llm_free/pipeline.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.retriever import search_bm25

HOLD_MSG = "（候補は見つかりましたが、出典URLが無いものは回答保留にしてください）"

def format_result(res):
    lines = []
    for r in res:
        url = r.get("url") or ""
        head = f"■ {r.get('title')} [{r.get('section')}]  score={r['score']:.3f}"
        body = f"  {r['snippet']}"
        tail = f"  出典URL: {url if url else 'なし'}"
        lines.append("\n".join([head, body, tail]))
    return "\n\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('使い方: python llm_free/pipeline.py "質問文"')
        sys.exit(1)
    q = sys.argv[1]
    res = search_bm25(q, top_k=8)
    if not res:
        print("候補が見つかりませんでした。表現や年度を変えて再検索してください。")
        sys.exit(0)
    if not (res[0].get("url") or ""):
        print(HOLD_MSG)
    print(format_result(res))
