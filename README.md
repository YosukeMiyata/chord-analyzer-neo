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
- tensorflow 2.13.0 (ChordAI機械学習モデル用)
- onnxruntime 1.24.1
- scikit-learn 1.8.0
- openai-whisper (歌詞書き起こし用)
- demucs (ボーカル分離用)

## セットアップ

### 前提条件

- Node.js 18+
- Python 3.11+ (Python 3.13はTensorFlowと互換性がないため使用不可)
- Rust (Tauri用)

### インストール

```bash
# Python依存関係のインストール
pip install -r requirements.txt

# フロントエンド依存関係のインストール
npm install
```

### ChordAIモデルのセットアップ

このアプリケーションは、コード認識にChordAI機械学習モデルを使用します。

1. **モデルファイルのダウンロード**
   - ChordAIリポジトリから最新リリースをダウンロード: https://github.com/anime-song/ChordAI/releases
   - `ChordAI.zip`をダウンロードして解凍

2. **モデルファイルの配置**
   ```bash
   # プロジェクトルートにmodelsディレクトリを作成
   mkdir -p models/chordai
   
   # ChordAI.zipから以下のファイルをコピー
   # models/ ディレクトリの内容を models/chordai/ にコピー
   # 必要なファイル:
   #   - saved_model.pb
   #   - variables/variables.data-00000-of-00001
   #   - variables/variables.index
   ```

3. **モデルファイルの確認**
   ```bash
   # 以下のファイルが存在することを確認
   ls -la models/chordai/
   # saved_model.pb
   # variables/
   ```

### 開発サーバーの起動

```bash
npm run tauri dev
```

## ライセンス

MIT License
