# Chord Analyzer Neo

ローカルで完結する楽曲のコード解析ツール

## 概要

chord-analyzer-neoは、音声ファイルからコード進行を自動推定し、演奏者の練習とアドリブをサポートするデスクトップアプリケーションです。

## 主な機能

- 音声ファイルからのコード進行自動推定
- 7th、9th、11th、13th対応
- 分数コード対応
- 歌詞の自動書き起こし（Whisper）
- 歌詞とコードの同期表示
- コードごとの推奨スケール表示
- ユーザーによるコード修正機能
- 複数モデルの切り替え

## 技術スタック

### フロントエンド
- Tauri 2.x
- React 19.x

### バックエンド
- Python 3.11+
- librosa 0.11.0
- tensorflow-cpu 2.13.0
- onnxruntime 1.24.1
- scikit-learn 1.8.0
- openai-whisper
- demucs

## セットアップ

### 前提条件

- Node.js 18+
- Python 3.11+
- Rust (Tauri用)

### インストール

```bash
# Python依存関係のインストール
pip install -r requirements.txt

# フロントエンド依存関係のインストール
npm install

# 開発サーバーの起動
npm run tauri dev
```

## ライセンス

MIT License
