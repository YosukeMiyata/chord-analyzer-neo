# 評価システム使用ガイド

## 概要

このガイドでは、実際の楽曲データを使って評価システムをテストする方法を説明します。

## 準備

### 1. テストデータディレクトリの作成

```bash
mkdir -p test_data/audio
mkdir -p test_data/ground_truth
```

### 2. 音声ファイルの配置

`test_data/audio/` ディレクトリに音声ファイルを配置してください。

対応フォーマット:
- `.mp3`
- `.wav`
- `.flac`
- `.m4a`
- `.ogg`
- `.aac`

例:
```
test_data/audio/
├── song1.mp3
├── song2.wav
└── song3.mp3
```

### 3. 正解データファイルの作成

`test_data/ground_truth/` ディレクトリに、音声ファイルと同じ名前（拡張子は異なる）の正解データファイルを作成してください。

対応フォーマット:
- `.txt`
- `.lab`
- `.chord`
- `.chords`

例:
```
test_data/ground_truth/
├── song1.txt
├── song2.txt
└── song3.txt
```

### 4. 正解データのフォーマット

評価システムは3種類のフォーマットに対応しています：

#### フォーマット1: コード進行のみ
```
[D][A][Bm7][G][D][A]
```

#### フォーマット2: 歌詞+コード
```
涙[D]があふれ[A]る[Bm7]夜に[G]
```

#### フォーマット3: 歌詞のみ（コードなし）
```
涙があふれる夜に
```
※ このフォーマットの場合、評価はスキップされます

## 使用方法

### 基本的な使い方

```python
from pathlib import Path
from src.evaluation import BenchmarkTool

# ベンチマークツールの初期化
tool = BenchmarkTool()

# ベンチマークの実行
results = tool.run_benchmark(
    audio_dir=Path("test_data/audio"),
    ground_truth_dir=Path("test_data/ground_truth")
)

# JSONレポートの生成
tool.generate_report(
    results=results,
    output_path=Path("evaluation_report.json"),
    format='json'
)

# Markdownレポートの生成
tool.generate_report(
    results=results,
    output_path=Path("evaluation_report.md"),
    format='markdown'
)

print(f"✓ {len(results)}曲の評価が完了しました")
```

### デモスクリプトの実行

既存のデモスクリプトを実行して、評価システムの動作を確認できます：

```bash
python examples/evaluation_demo.py
```

このスクリプトは以下を実行します：
1. パーサーのデモ（3種類のフォーマット）
2. 評価器のデモ（完全一致、部分一致、長さ違い）
3. ベンチマークツールのセットアップ確認
4. 集計統計のデモ
5. JSONレポート生成のデモ

### Markdownレポートのデモ

```bash
python examples/markdown_report_demo.py
```

このスクリプトは：
- サンプルデータでMarkdownレポートを生成
- レポートのプレビューを表示
- `evaluation_report.md` を生成

## 評価指標の説明

評価システムは5つの指標を計算します：

### 1. Sequence Accuracy（シーケンス精度）
- コード進行全体が完全に一致する確率
- 範囲: 0.0 〜 1.0（0% 〜 100%）

### 2. Root Accuracy（ルート音精度）
- ルート音（根音）が一致する確率
- 例: "D" と "Dm7" → ルート音は一致
- 範囲: 0.0 〜 1.0（0% 〜 100%）

### 3. Quality Accuracy（コード品質精度）
- コードの品質（メジャー、マイナー、7thなど）が一致する確率
- 範囲: 0.0 〜 1.0（0% 〜 100%）

### 4. DTW Distance（DTW距離）
- Dynamic Time Warpingによる時間的ずれを考慮した距離
- 値が小さいほど良い（0.0が最良）
- 範囲: 0.0 〜 ∞

### 5. Exact Match Rate（完全一致率）
- 個々のコードが完全に一致する確率
- 範囲: 0.0 〜 1.0（0% 〜 100%）

## レポートの見方

### JSONレポート

```json
{
  "summary": {
    "total_songs": 3,
    "aggregate_statistics": {
      "root_accuracy_mean": 0.85,
      "root_accuracy_std": 0.05,
      "root_accuracy_min": 0.80,
      "root_accuracy_max": 0.90,
      ...
    }
  },
  "detailed_results": [
    {
      "song_name": "song1",
      "metrics": {
        "sequence_accuracy": 0.8,
        "root_accuracy": 0.9,
        ...
      },
      "predicted_chords": ["D", "A", "Bm7", "G"],
      "ground_truth_chords": ["D", "A", "Bm7", "G"],
      "processing_time": 2.5
    }
  ]
}
```

### Markdownレポート

```markdown
# Chord Recognition Evaluation Report

## Summary

**Total Songs Processed:** 3

## Aggregate Statistics

| Metric | Mean | Std Dev | Min | Max |
|--------|------|---------|-----|-----|
| Root Accuracy | 85.00% | 5.00% | 80.00% | 90.00% |
...

## Detailed Results by Song

### 1. song1

| Metric | Value |
|--------|-------|
| Root Accuracy | 90.00% |
...

**Predicted Chords:**

`D | A | Bm7 | G`

**Ground Truth Chords:**

`D | A | Bm7 | G`
```

## トラブルシューティング

### エラー: "No file pairs found"

**原因**: 音声ファイルと正解データファイルの名前が一致していない

**解決方法**:
- ファイル名（拡張子を除く）が完全に一致していることを確認
- 例: `song1.mp3` → `song1.txt`

### エラー: "No chords found in ground truth file"

**原因**: 正解データファイルにコード情報が含まれていない

**解決方法**:
- ファイルの内容を確認
- 対応フォーマット（`[D][A][Bm7]` など）で記述されているか確認

### エラー: "Failed to process audio file"

**原因**: 音声ファイルの読み込みまたは処理に失敗

**解決方法**:
- 音声ファイルが破損していないか確認
- 対応フォーマットであることを確認
- ファイルサイズが適切であることを確認

### 警告: "No ground truth file found for audio"

**原因**: 音声ファイルに対応する正解データファイルがない

**影響**: その音声ファイルはスキップされますが、他のファイルの処理は継続されます

**解決方法**:
- 対応する正解データファイルを作成
- または、その音声ファイルを削除

## 次のステップ

### 実際の楽曲でテスト

1. 音声ファイルを `test_data/audio/` に配置
2. 正解データを `test_data/ground_truth/` に作成
3. 以下のスクリプトを実行:

```python
from pathlib import Path
from src.evaluation import BenchmarkTool

tool = BenchmarkTool()
results = tool.run_benchmark(
    audio_dir=Path("test_data/audio"),
    ground_truth_dir=Path("test_data/ground_truth")
)

# 両方のフォーマットでレポート生成
tool.generate_report(results, Path("evaluation_report.json"), format='json')
tool.generate_report(results, Path("evaluation_report.md"), format='markdown')

print(f"✓ 評価完了: {len(results)}曲")
print(f"✓ レポート生成: evaluation_report.json, evaluation_report.md")
```

### パラメータ最適化（今後実装予定）

Task 14で実装予定のパラメータ最適化機能を使用すると、最適なシステムパラメータを自動的に見つけることができます。

## サンプルデータの作成例

### 簡単なテストケース

**test_data/audio/simple_test.mp3** (任意の音声ファイル)

**test_data/ground_truth/simple_test.txt**:
```
[C][G][Am][F][C][G][F][C]
```

このような簡単なコード進行から始めることをお勧めします。

## 参考情報

- 設計ドキュメント: `.kiro/specs/evaluation-system/design.md`
- 要件ドキュメント: `.kiro/specs/evaluation-system/requirements.md`
- タスクリスト: `.kiro/specs/evaluation-system/tasks.md`
- デモスクリプト: `examples/evaluation_demo.py`
- Markdownデモ: `examples/markdown_report_demo.py`

## 注意事項

1. **ファイル名の一致**: 音声ファイルと正解データファイルの名前（拡張子を除く）は完全に一致している必要があります
2. **エンコーディング**: 正解データファイルはUTF-8エンコーディングで保存してください
3. **処理時間**: 音声ファイルのサイズや数によっては、処理に時間がかかる場合があります
4. **エラーハンドリング**: 個別のファイルでエラーが発生しても、他のファイルの処理は継続されます

## 質問・問題報告

評価システムの使用中に問題が発生した場合は、以下の情報を含めて報告してください：

1. エラーメッセージ
2. 使用した音声ファイルのフォーマットとサイズ
3. 正解データファイルの内容（最初の数行）
4. 実行したコマンドまたはスクリプト
