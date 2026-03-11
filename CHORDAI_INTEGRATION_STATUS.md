# ChordAI統合の現状と次のステップ

## 現状サマリー

### 実施した作業
1. ChordAIモデル（anime-song/ChordAI v0.02-alpha）をダウンロードし、`models/chordai/`に配置
2. ChordAI統合のための実装を完了：
   - `src/chordai_loader.py` - モデルローダー
   - `src/chordai_inference.py` - 推論エンジン（CQT特徴量ベース）
   - `src/chordai_mapper.py` - 出力マッパー
   - `src/chordai_models.py` - データモデル
3. `src/chord_estimation.py`を修正し、ChordAIを統合
4. 元の`_simple_chord_recognition`メソッド（テンプレートマッチング）を削除
5. テストを実装・更新（219/227テスト合格、96.5%）

### 問題点
ChordAIモデルが実際の音楽ファイルで正しく動作しない：
- 全てのフレームで「N.C.」（No Chord）または「C」（Cメジャー）のみを検出
- 信頼度が非常に低い（5.62%）
- フレーム間の変化がほとんどない

**原因**: モデルの正しい入力形式・前処理方法が不明
- 公式リポジトリにはコンパイル済みアプリのみで、実装コードがない
- CQTパラメータ（hop_length、bins_per_octave等）が不明
- 正規化方法が不明

### テストした代替案
1. **madmom** - インストールに失敗（Python 3.11互換性問題）
2. **librosa テンプレートマッチング** - 動作確認済み、良好な結果

## 次のステップ

### 推奨アプローチ
テンプレートマッチング方式を復元し、ChordAIと選択可能にする：

1. **元の`_simple_chord_recognition`メソッドを復元**
   - Gitの履歴から元のコードを取得
   - または`test_librosa_chords.py`のロジックを参考に再実装

2. **認識方式を選択可能にする**
   ```python
   def __init__(self, model_path: Optional[Path] = None, use_chordai: bool = False):
       self.use_chordai = use_chordai
       if use_chordai:
           # ChordAI初期化
       else:
           # テンプレートマッチング初期化
   ```

3. **`estimate_chords`メソッドで分岐**
   ```python
   if self.use_chordai:
       chord_segments = self._chordai_recognition(chroma, sample_rate)
   else:
       chord_segments = self._simple_chord_recognition(chroma, sample_rate)
   ```

4. **テストを更新**
   - デフォルトはテンプレートマッチング（`use_chordai=False`）
   - ChordAI関連テストは`use_chordai=True`で実行

### 実装ファイル

#### 復元が必要なファイル
- `src/chord_estimation.py` - `_simple_chord_recognition`メソッドを追加

#### 参考ファイル
- `test_librosa_chords.py` - 動作するテンプレートマッチングの実装例
- Git履歴: ChordAI統合前のコミット

### テンプレートマッチングの実装概要

```python
def _simple_chord_recognition(
    self,
    chroma: np.ndarray,
    sample_rate: int
) -> List[ChordSegment]:
    """Simple template matching chord recognition
    
    Args:
        chroma: Chroma features (12, n_frames)
        sample_rate: Audio sample rate
        
    Returns:
        List of ChordSegment objects
    """
    # 1. コードテンプレートを作成（24種類: 12 major + 12 minor）
    chord_templates = self._create_chord_templates()
    
    # 2. 各フレームで最も近いテンプレートを検索
    n_frames = chroma.shape[1]
    frame_duration = 512 / sample_rate  # hop_length / sr
    
    chords = []
    for i in range(n_frames):
        frame_chroma = chroma[:, i]
        
        # 正規化
        if np.sum(frame_chroma) > 0:
            frame_chroma = frame_chroma / np.linalg.norm(frame_chroma)
        
        # 最適なコードを検索（コサイン類似度）
        best_chord = None
        best_score = -1
        
        for chord_name, template in chord_templates.items():
            score = np.dot(frame_chroma, template)
            if score > best_score:
                best_score = score
                best_chord = chord_name
        
        time = i * frame_duration
        chords.append((time, best_chord, best_score))
    
    # 3. 連続する同じコードをマージ
    merged_chords = self._merge_consecutive_chords(chords)
    
    # 4. ChordSegmentオブジェクトに変換
    chord_segments = []
    for start, end, chord_name, confidence in merged_chords:
        # chord_nameをroot, qualityに分解
        root, quality = self._parse_chord_name(chord_name)
        
        segment = ChordSegment(
            start_time=start,
            end_time=end,
            root=root,
            quality=ChordQuality(quality),
            bass_note=None,
            confidence=confidence,
            extensions=[]
        )
        chord_segments.append(segment)
    
    return chord_segments
```

### コードテンプレート作成

```python
def _create_chord_templates(self) -> Dict[str, np.ndarray]:
    """Create chord templates for template matching"""
    templates = {}
    
    # Major chord: root, major third, perfect fifth
    major_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
    
    # Minor chord: root, minor third, perfect fifth
    minor_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
    
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    for i, note in enumerate(note_names):
        # Major
        templates[note] = np.roll(major_template, i)
        templates[note] = templates[note] / np.linalg.norm(templates[note])
        
        # Minor
        templates[f"{note}m"] = np.roll(minor_template, i)
        templates[f"{note}m"] = templates[f"{note}m"] / np.linalg.norm(templates[f"{note}m"])
    
    return templates
```

## 将来の改善案

### ChordAIの再挑戦
1. 元の実装コードを見つける（anime-song/auto-chord-tracker等）
2. 正しいCQTパラメータを特定
3. 適切な前処理・正規化方法を実装

### 他のモデルの検討
1. **BTC (Bi-Directional Transformer)** - ISMIR 2019
   - GitHub: https://github.com/jayg996/BTC-ISMIR19
   - 学習済みモデルの入手が必要

2. **autochord** - PyPIパッケージ
   - 25コードクラス（major, minor, no-chord）
   - Bi-LSTM-CRF

3. **madmom** - Python 3.11対応版を待つ

## ファイル一覧

### 実装ファイル
- `src/chord_estimation.py` - メインモジュール（要修正）
- `src/chordai_loader.py` - ChordAIローダー（保持）
- `src/chordai_inference.py` - ChordAI推論（保持）
- `src/chordai_mapper.py` - ChordAIマッパー（保持）
- `src/chordai_models.py` - データモデル（保持）

### テストファイル
- `tests/test_chord_estimation.py` - メインテスト
- `tests/test_chordai_*.py` - ChordAI関連テスト（保持）

### デバッグ・検証ファイル
- `test_real_audio.py` - 実音楽ファイルテスト
- `test_librosa_chords.py` - テンプレートマッチング動作確認
- `debug_inference.py` - ChordAIデバッグ
- `inspect_model.py` - モデル仕様確認

### ドキュメント
- `.kiro/specs/chordai-model-integration/` - 統合仕様
- `RESEARCH_FINDINGS.md` - ChordAI調査結果
- `TASK_13_SUMMARY.md` - タスク13完了サマリー

## 次のセッションでの作業手順

1. Gitで元の`_simple_chord_recognition`実装を確認
2. `src/chord_estimation.py`に`_simple_chord_recognition`を復元
3. `__init__`に`use_chordai`パラメータを追加
4. `estimate_chords`で認識方式を分岐
5. テストを実行して動作確認
6. 実音楽ファイルでテスト
7. デフォルトをテンプレートマッチングに設定

## 参考コマンド

```bash
# 元の実装を確認
git log --all --oneline --graph src/chord_estimation.py
git show <commit-hash>:src/chord_estimation.py

# テスト実行
python -m pytest tests/test_chord_estimation.py -v

# 実音楽ファイルテスト
python test_real_audio.py "/Users/yousuke/Desktop/真夏の果実.mp3"
```
