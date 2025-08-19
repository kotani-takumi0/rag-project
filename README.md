# RAG プロジェクト（BM25 vs ベクトル検索）

## 概要
本プロジェクトは、行政の政策データ（行政事業レビューシート）を対象に、**検索手法の比較**を行うものです。  
以下の 2 手法を実装し、検索性能・使い勝手の違いを検証します。

- **BM25**：従来のスパース検索手法  
- **ベクトル検索**：埋め込みベクトル + FAISS による意味検索（OpenAI Embeddings ）

将来的には、この基盤の上に **RAG（Retrieval-Augmented Generation）** を構築することを目標とします。

## 主要機能
- 行政レビューシート等のテキストを対象とした前処理（チャンク化など）
- **BM25 検索**の実装
- **埋め込み + FAISS 検索**の実装
- コマンドラインからの検索比較ツール

## ディレクトリ構成
```
.
├── data/                       # 入力データ（例: policy_chunks.jsonl など）
├── scripts/
│   ├── search_bm25.py          # BM25 検索
│   ├── search_embed_chunks.py  # Embedding + FAISS 検索
│   └── evaluate.py             # 検索性能評価
├── notebooks/                  # 実験・分析用ノートブック
├── requirements.txt            # 依存パッケージ
└── README.md                   # 本ファイル
```

## セットアップ
```bash
git clone https://github.com/kotani-takumi0/rag-project.git
cd rag-project

# 仮想環境の作成と有効化
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# 依存パッケージのインストール
pip install -r requirements.txt
```

> ※ 埋め込みの生成に外部 API（例: OpenAI）を使用する場合は、必要に応じて環境変数（`OPENAI_API_KEY` など）を設定してください。  
> 既に作成済みの埋め込みを読み込む場合は、API キーは不要です。

## データの配置
- 検索対象のテキストを **JSONL（例: `policy_chunks.jsonl`）** などで `data/` 配下に配置してください。
- スクリプト内部のパスやファイル名は、手元の構成に合わせて調整可能です。

## 使い方

### 1) BM25 検索
```bash
python scripts/search_bm25.py --query "勤務医の働き方改革" --k 5
```

### 2) 埋め込み検索（FAISS）
```bash
python scripts/search_embed_chunks.py --query "勤務医の働き方改革" --k 5
```


## 今後の展望
- 評価指標の拡充（Precision@k, Recall@k, nDCG など）
- RAG（Retrieval-Augmented Generation）への拡張
- BM25 と FAISS の **速度**・**メモリ使用量** の比較
- 行政職員向けの政策情報検索支援ツールとしての UI/UX 改善

## ライセンス
MIT License
