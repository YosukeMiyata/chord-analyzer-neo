"""
前処理のデバッグスクリプト

集約処理で何が起きているかを詳細に確認します。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.evaluation import BenchmarkTool, GroundTruthParser
from src.evaluation.preprocessing import (
    PreprocessingPipeline,
    PreprocessingConfig,
    NormalizationMode,
    AggregationStrategy,
    ChordWithTimestamp
)


def main():
    """前処理のデバッグ"""
    
    # ファイルパス
    audio_path = Path("test_data/audio/真夏の果実.mp3")
    gt_path = Path("test_data/ground_truth/真夏の果実.txt")
    
    # 正解データの読み込み
    parser = GroundTruthParser()
    with open(gt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    gt_annotations = parser.parse(content)
    print(f"正解データ: {len(gt_annotations)}個のコード")
    print(f"最初の10個: {[ann.chord for ann in gt_annotations[:10]]}")
    print(f"位置情報: {[ann.position for ann in gt_annotations[:10]]}")
    
    # ベンチマークツールで予測コードを取得
    tool = BenchmarkTool()
    
    # 音声ファイルを処理（前処理なし）
    print("\n音声ファイルを処理中...")
    result = tool.process_single_song(
        audio_path,
        gt_path,
        enable_preprocessing=False
    )
    
    print(f"\n予測コード: {len(result.predicted_chords)}個")
    print(f"最初の10個: {result.predicted_chords[:10]}")
    
    # 予測コードのタイムスタンプを取得
    # BenchmarkToolのprocess_single_songから取得する必要がある
    # ここでは簡易的に等間隔と仮定
    audio_duration = 240.0  # 仮の長さ（秒）
    pred_timestamps = [i * (audio_duration / len(result.predicted_chords)) 
                      for i in range(len(result.predicted_chords))]
    
    print(f"\n予測タイムスタンプ（最初の10個）: {pred_timestamps[:10]}")
    
    # 正解データのタイムスタンプ（位置情報を使用）
    gt_timestamps = [ann.position for ann in gt_annotations]
    print(f"\n正解タイムスタンプ（最初の10個）: {gt_timestamps[:10]}")
    
    # 前処理パイプラインの設定
    config = PreprocessingConfig(
        normalization_mode=NormalizationMode.SLASH,
        aggregation_strategy=AggregationStrategy.MOST_FREQUENT,
        aggregation_tolerance=0.1,
        enable_normalization=True,
        enable_aggregation=True
    )
    pipeline = PreprocessingPipeline(config)
    
    # 正規化のテスト
    print("\n=== 正規化テスト ===")
    test_chords = result.predicted_chords[:10]
    print(f"正規化前: {test_chords}")
    normalized = pipeline.normalizer.normalize_batch(test_chords)
    print(f"正規化後: {normalized}")
    
    # 集約のテスト
    print("\n=== 集約テスト ===")
    print(f"予測コード数: {len(result.predicted_chords)}")
    print(f"正解コード数: {len(gt_annotations)}")
    print(f"予測タイムスタンプ範囲: {pred_timestamps[0]:.2f} - {pred_timestamps[-1]:.2f}")
    print(f"正解タイムスタンプ範囲: {gt_timestamps[0]:.2f} - {gt_timestamps[-1]:.2f}")
    
    # ChordWithTimestampオブジェクトを作成
    pred_chords_with_ts = [
        ChordWithTimestamp(chord=chord, timestamp=ts)
        for chord, ts in zip(result.predicted_chords, pred_timestamps)
    ]
    
    gt_chords_with_ts = [
        ChordWithTimestamp(chord=ann.chord, timestamp=ann.position)
        for ann in gt_annotations
    ]
    
    # 前処理を適用
    print("\n前処理を適用中...")
    processed_pred, processed_gt = pipeline.process(
        pred_chords_with_ts,
        gt_chords_with_ts
    )
    
    print(f"\n処理後の予測コード数: {len(processed_pred)}")
    print(f"処理後の正解コード数: {len(processed_gt)}")
    print(f"\n処理後の予測コード（最初の20個）:")
    for i, chord in enumerate(processed_pred[:20]):
        print(f"  {i}: {chord.chord} @ {chord.timestamp:.2f}s")
    
    print(f"\n処理後の正解コード（最初の20個）:")
    for i, chord in enumerate(processed_gt[:20]):
        print(f"  {i}: {chord.chord} @ {chord.timestamp:.2f}s")
    
    # 集約の詳細を確認
    print("\n=== 集約の詳細確認 ===")
    print(f"集約戦略: {config.aggregation_strategy.value}")
    print(f"許容誤差: {config.aggregation_tolerance}秒")
    
    # 最初のいくつかのインターバルを手動で確認
    for i in range(min(5, len(gt_timestamps))):
        start_time = gt_timestamps[i]
        end_time = gt_timestamps[i + 1] if i + 1 < len(gt_timestamps) else float('inf')
        
        # このインターバル内のコードを収集
        chords_in_interval = []
        for j, ts in enumerate(pred_timestamps):
            if start_time - config.aggregation_tolerance <= ts < end_time + config.aggregation_tolerance:
                chords_in_interval.append((result.predicted_chords[j], ts))
        
        print(f"\nインターバル {i}: [{start_time:.2f}, {end_time:.2f})")
        print(f"  正解コード: {gt_annotations[i].chord}")
        print(f"  インターバル内の予測コード数: {len(chords_in_interval)}")
        if chords_in_interval:
            print(f"  最初の5個: {[c for c, _ in chords_in_interval[:5]]}")
            # 最頻値を計算
            from collections import Counter
            counter = Counter([c for c, _ in chords_in_interval])
            most_common = counter.most_common(1)[0]
            print(f"  最頻値: {most_common[0]} (出現回数: {most_common[1]})")


if __name__ == "__main__":
    main()
