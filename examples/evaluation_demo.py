"""
評価システムのデモスクリプト

実際の楽曲データを使って評価システムの動作を確認します。
"""

from pathlib import Path
from src.evaluation import BenchmarkTool, GroundTruthParser, Evaluator

def demo_parser():
    """パーサーのデモ"""
    print("=" * 60)
    print("1. Ground Truth Parser のデモ")
    print("=" * 60)
    
    parser = GroundTruthParser()
    
    # コード進行のみフォーマット
    chord_only = "[D][A][Bm7][G][D][A]"
    print(f"\n入力 (コード進行のみ): {chord_only}")
    annotations = parser.parse(chord_only)
    print(f"パース結果: {len(annotations)}個のコード")
    for ann in annotations:
        print(f"  - {ann.chord} (位置: {ann.position})")
    
    # 歌詞+コードフォーマット
    lyrics_with_chords = "涙[D]があふれ[A]る[Bm7]夜に[G]"
    print(f"\n入力 (歌詞+コード): {lyrics_with_chords}")
    annotations = parser.parse(lyrics_with_chords)
    print(f"パース結果: {len(annotations)}個のコード")
    for ann in annotations:
        print(f"  - {ann.chord} (文字位置: {ann.position})")

def demo_evaluator():
    """評価器のデモ"""
    print("\n" + "=" * 60)
    print("2. Evaluator のデモ")
    print("=" * 60)
    
    evaluator = Evaluator()
    
    # 完全一致のケース
    predicted = ["D", "A", "Bm7", "G"]
    ground_truth = ["D", "A", "Bm7", "G"]
    
    print(f"\n予測: {predicted}")
    print(f"正解: {ground_truth}")
    
    metrics = evaluator.evaluate(predicted, ground_truth)
    print("\n評価結果:")
    print(f"  - シーケンス精度: {metrics.sequence_accuracy:.2%}")
    print(f"  - ルート音精度: {metrics.root_accuracy:.2%}")
    print(f"  - コード品質精度: {metrics.quality_accuracy:.2%}")
    print(f"  - DTW距離: {metrics.dtw_distance:.3f}")
    print(f"  - 完全一致率: {metrics.exact_match_rate:.2%}")
    
    # 部分一致のケース
    predicted = ["D", "A", "Em", "G"]
    ground_truth = ["D", "AonC#", "Bm7", "G"]
    
    print(f"\n予測: {predicted}")
    print(f"正解: {ground_truth}")
    
    metrics = evaluator.evaluate(predicted, ground_truth)
    print("\n評価結果:")
    print(f"  - シーケンス精度: {metrics.sequence_accuracy:.2%}")
    print(f"  - ルート音精度: {metrics.root_accuracy:.2%}")
    print(f"  - コード品質精度: {metrics.quality_accuracy:.2%}")
    print(f"  - DTW距離: {metrics.dtw_distance:.3f}")
    print(f"  - 完全一致率: {metrics.exact_match_rate:.2%}")
    
    # 長さが異なるケース（アライメント機能のデモ）
    predicted = ["D", "A", "G"]
    ground_truth = ["D", "A", "Bm7", "G"]
    
    print(f"\n予測: {predicted} (長さ: {len(predicted)})")
    print(f"正解: {ground_truth} (長さ: {len(ground_truth)})")
    print("※ 長さが異なる場合、自動的にアライメントされます")
    
    metrics = evaluator.evaluate(predicted, ground_truth)
    print("\n評価結果:")
    print(f"  - シーケンス精度: {metrics.sequence_accuracy:.2%}")
    print(f"  - ルート音精度: {metrics.root_accuracy:.2%}")
    print(f"  - コード品質精度: {metrics.quality_accuracy:.2%}")
    print(f"  - DTW距離: {metrics.dtw_distance:.3f}")
    print(f"  - 完全一致率: {metrics.exact_match_rate:.2%}")

def demo_benchmark_setup():
    """ベンチマークツールのセットアップデモ"""
    print("\n" + "=" * 60)
    print("3. Benchmark Tool のセットアップ")
    print("=" * 60)
    
    # テストデータディレクトリの確認
    audio_dir = Path("test_data/audio")
    gt_dir = Path("test_data/ground_truth")
    
    print(f"\n音声ファイルディレクトリ: {audio_dir}")
    print(f"正解データディレクトリ: {gt_dir}")
    
    if not audio_dir.exists() or not gt_dir.exists():
        print("\n⚠️  テストデータディレクトリが見つかりません")
        print("\n以下の手順でテストデータを準備してください:")
        print("1. test_data/audio/ に音声ファイル (.mp3, .wav など) を配置")
        print("2. test_data/ground_truth/ に対応する正解データファイル (.txt) を配置")
        print("   - ファイル名は音声ファイルと同じにしてください")
        print("   - 例: song1.mp3 → song1.txt")
        print("\n正解データのフォーマット例:")
        print("  [D][A][Bm7][G]  (コード進行のみ)")
        print("  または")
        print("  涙[D]があふれ[A]る  (歌詞+コード)")
        return False
    
    # ファイルペアの検出
    tool = BenchmarkTool()
    try:
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        print(f"\n✓ {len(pairs)}個のファイルペアを検出しました")
        
        if pairs:
            print("\n検出されたファイルペア:")
            for audio_path, gt_path in pairs:
                print(f"  - {audio_path.name} ↔ {gt_path.name}")
            return True
        else:
            print("\n⚠️  ファイルペアが見つかりませんでした")
            print("音声ファイルと正解データファイルの名前が一致しているか確認してください")
            return False
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        return False

def demo_aggregate_stats():
    """集計統計のデモ"""
    print("\n" + "=" * 60)
    print("4. 集計統計のデモ")
    print("=" * 60)
    
    from src.evaluation.models import BenchmarkResult, EvaluationMetrics
    
    # サンプルデータの作成
    results = [
        BenchmarkResult(
            song_name="song1",
            metrics=EvaluationMetrics(
                sequence_accuracy=1.0,
                root_accuracy=1.0,
                quality_accuracy=1.0,
                dtw_distance=0.0,
                exact_match_rate=1.0
            ),
            predicted_chords=["D", "A", "Bm7", "G"],
            ground_truth_chords=["D", "A", "Bm7", "G"],
            processing_time=1.5
        ),
        BenchmarkResult(
            song_name="song2",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.5,
                root_accuracy=0.8,
                quality_accuracy=0.6,
                dtw_distance=0.3,
                exact_match_rate=0.5
            ),
            predicted_chords=["C", "G", "Am", "F"],
            ground_truth_chords=["D", "A", "Bm7", "G"],
            processing_time=2.0
        ),
        BenchmarkResult(
            song_name="song3",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.0,
                root_accuracy=0.6,
                quality_accuracy=0.4,
                dtw_distance=0.5,
                exact_match_rate=0.3
            ),
            predicted_chords=["E", "B", "C#m", "A"],
            ground_truth_chords=["D", "A", "Bm7", "G"],
            processing_time=1.8
        )
    ]
    
    print(f"\n{len(results)}曲の評価結果から集計統計を計算:")
    
    tool = BenchmarkTool()
    aggregates = tool.aggregate_metrics(results)
    
    print("\n集計統計:")
    metrics = ['sequence_accuracy', 'root_accuracy', 'quality_accuracy', 
               'dtw_distance', 'exact_match_rate']
    
    for metric in metrics:
        mean = aggregates[f'{metric}_mean']
        std = aggregates[f'{metric}_std']
        min_val = aggregates[f'{metric}_min']
        max_val = aggregates[f'{metric}_max']
        
        metric_name = {
            'sequence_accuracy': 'シーケンス精度',
            'root_accuracy': 'ルート音精度',
            'quality_accuracy': 'コード品質精度',
            'dtw_distance': 'DTW距離',
            'exact_match_rate': '完全一致率'
        }[metric]
        
        if metric == 'dtw_distance':
            print(f"\n{metric_name}:")
            print(f"  平均: {mean:.3f}")
            print(f"  標準偏差: {std:.3f}")
            print(f"  最小: {min_val:.3f}")
            print(f"  最大: {max_val:.3f}")
        else:
            print(f"\n{metric_name}:")
            print(f"  平均: {mean:.2%}")
            print(f"  標準偏差: {std:.3f}")
            print(f"  最小: {min_val:.2%}")
            print(f"  最大: {max_val:.2%}")

def demo_json_report():
    """JSONレポート生成のデモ"""
    print("\n" + "=" * 60)
    print("5. JSONレポート生成のデモ")
    print("=" * 60)
    
    from src.evaluation.models import BenchmarkResult, EvaluationMetrics
    import json
    
    # サンプルデータの作成
    results = [
        BenchmarkResult(
            song_name="涙があふれる",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.8,
                root_accuracy=0.9,
                quality_accuracy=0.85,
                dtw_distance=0.15,
                exact_match_rate=0.75
            ),
            predicted_chords=["D", "A", "Bm7", "G"],
            ground_truth_chords=["D", "AonC#", "Bm7", "G"],
            processing_time=1.5
        )
    ]
    
    # レポート生成
    output_path = Path("test_data/demo_report.json")
    tool = BenchmarkTool()
    tool.generate_report(results, output_path, format='json')
    
    print(f"\n✓ JSONレポートを生成しました: {output_path}")
    
    # レポート内容の表示
    with open(output_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print("\nレポート内容:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

def main():
    """メイン関数"""
    print("\n" + "=" * 60)
    print("評価システム デモ")
    print("=" * 60)
    
    try:
        # 1. パーサーのデモ
        demo_parser()
        
        # 2. 評価器のデモ
        demo_evaluator()
        
        # 3. ベンチマークツールのセットアップ
        has_test_data = demo_benchmark_setup()
        
        # 4. 集計統計のデモ
        demo_aggregate_stats()
        
        # 5. JSONレポート生成のデモ
        demo_json_report()
        
        print("\n" + "=" * 60)
        print("デモ完了")
        print("=" * 60)
        
        if not has_test_data:
            print("\n💡 実際の音声ファイルでベンチマークを実行するには:")
            print("   1. test_data/audio/ に音声ファイルを配置")
            print("   2. test_data/ground_truth/ に正解データを配置")
            print("   3. 以下のコードを実行:")
            print("\n   from pathlib import Path")
            print("   from src.evaluation import BenchmarkTool")
            print("   ")
            print("   tool = BenchmarkTool()")
            print("   results = tool.run_benchmark(")
            print("       audio_dir=Path('test_data/audio'),")
            print("       ground_truth_dir=Path('test_data/ground_truth')")
            print("   )")
            print("   tool.generate_report(results, Path('evaluation_report.json'))")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
