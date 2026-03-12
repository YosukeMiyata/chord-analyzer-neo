"""
前処理機能を実データでテストするスクリプト

このスクリプトは前処理機能の効果を検証します:
1. 前処理なしでベンチマークを実行
2. 前処理ありでベンチマークを実行
3. 結果を比較して改善効果を表示

使用方法:
1. test_data/audio/ に音声ファイルを配置
2. test_data/ground_truth/ に正解データファイルを配置
3. このスクリプトを実行: python examples/test_preprocessing_with_real_data.py
"""

import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import BenchmarkTool
from src.evaluation.preprocessing import (
    PreprocessingPipeline,
    PreprocessingConfig,
    NormalizationMode,
    AggregationStrategy
)
from src.evaluation.models import BenchmarkResult


def print_header(title: str):
    """ヘッダーを表示"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_metrics_comparison(
    results_without: List[BenchmarkResult],
    results_with: List[BenchmarkResult],
    tool: BenchmarkTool
):
    """メトリクスの比較を表示"""
    
    # 集計統計の計算
    agg_without = tool.aggregate_metrics(results_without)
    agg_with = tool.aggregate_metrics(results_with)
    
    print("\n【集計統計の比較】")
    print(f"  処理楽曲数: {len(results_without)}曲")
    
    # ルート音精度
    root_diff = agg_with['root_accuracy_mean'] - agg_without['root_accuracy_mean']
    root_symbol = "↑" if root_diff > 0 else "↓" if root_diff < 0 else "="
    print(f"\n  ルート音精度:")
    print(f"    前処理なし: {agg_without['root_accuracy_mean']:.2%}")
    print(f"    前処理あり: {agg_with['root_accuracy_mean']:.2%}")
    print(f"    差分: {root_symbol} {abs(root_diff):.2%}")
    
    # コード品質精度
    quality_diff = agg_with['quality_accuracy_mean'] - agg_without['quality_accuracy_mean']
    quality_symbol = "↑" if quality_diff > 0 else "↓" if quality_diff < 0 else "="
    print(f"\n  コード品質精度:")
    print(f"    前処理なし: {agg_without['quality_accuracy_mean']:.2%}")
    print(f"    前処理あり: {agg_with['quality_accuracy_mean']:.2%}")
    print(f"    差分: {quality_symbol} {abs(quality_diff):.2%}")
    
    # DTW距離（小さい方が良い）
    dtw_diff = agg_without['dtw_distance_mean'] - agg_with['dtw_distance_mean']
    dtw_symbol = "↑" if dtw_diff > 0 else "↓" if dtw_diff < 0 else "="
    print(f"\n  DTW距離:")
    print(f"    前処理なし: {agg_without['dtw_distance_mean']:.4f}")
    print(f"    前処理あり: {agg_with['dtw_distance_mean']:.4f}")
    print(f"    改善: {dtw_symbol} {abs(dtw_diff):.4f}")
    
    # 完全一致率
    exact_diff = agg_with['exact_match_rate_mean'] - agg_without['exact_match_rate_mean']
    exact_symbol = "↑" if exact_diff > 0 else "↓" if exact_diff < 0 else "="
    print(f"\n  完全一致率:")
    print(f"    前処理なし: {agg_without['exact_match_rate_mean']:.2%}")
    print(f"    前処理あり: {agg_with['exact_match_rate_mean']:.2%}")
    print(f"    差分: {exact_symbol} {abs(exact_diff):.2%}")


def print_song_comparison(
    results_without: List[BenchmarkResult],
    results_with: List[BenchmarkResult]
):
    """楽曲ごとの比較を表示"""
    
    print_header("楽曲ごとの詳細比較")
    
    for i, (res_without, res_with) in enumerate(zip(results_without, results_with), 1):
        print(f"\n【{i}. {res_without.song_name}】")
        
        # 予測コード数の変化
        pred_diff = len(res_with.predicted_chords) - len(res_without.predicted_chords)
        print(f"  予測コード数: {len(res_without.predicted_chords)} → {len(res_with.predicted_chords)} (差分: {pred_diff:+d})")
        print(f"  正解コード数: {len(res_without.ground_truth_chords)}")
        
        # ルート音精度
        root_diff = res_with.metrics.root_accuracy - res_without.metrics.root_accuracy
        root_symbol = "↑" if root_diff > 0 else "↓" if root_diff < 0 else "="
        print(f"  ルート音精度: {res_without.metrics.root_accuracy:.2%} → {res_with.metrics.root_accuracy:.2%} ({root_symbol} {abs(root_diff):.2%})")
        
        # コード品質精度
        quality_diff = res_with.metrics.quality_accuracy - res_without.metrics.quality_accuracy
        quality_symbol = "↑" if quality_diff > 0 else "↓" if quality_diff < 0 else "="
        print(f"  コード品質精度: {res_without.metrics.quality_accuracy:.2%} → {res_with.metrics.quality_accuracy:.2%} ({quality_symbol} {abs(quality_diff):.2%})")
        
        # DTW距離
        dtw_diff = res_without.metrics.dtw_distance - res_with.metrics.dtw_distance
        dtw_symbol = "↑" if dtw_diff > 0 else "↓" if dtw_diff < 0 else "="
        print(f"  DTW距離: {res_without.metrics.dtw_distance:.4f} → {res_with.metrics.dtw_distance:.4f} ({dtw_symbol} {abs(dtw_diff):.4f})")
        
        # 完全一致率
        exact_diff = res_with.metrics.exact_match_rate - res_without.metrics.exact_match_rate
        exact_symbol = "↑" if exact_diff > 0 else "↓" if exact_diff < 0 else "="
        print(f"  完全一致率: {res_without.metrics.exact_match_rate:.2%} → {res_with.metrics.exact_match_rate:.2%} ({exact_symbol} {abs(exact_diff):.2%})")


def main():
    """前処理機能を実データでテスト"""
    
    print_header("前処理機能の実データテスト")
    
    # ディレクトリパスの設定
    audio_dir = Path("test_data/audio")
    ground_truth_dir = Path("test_data/ground_truth")
    
    # ディレクトリの存在確認
    if not audio_dir.exists():
        print(f"\n❌ エラー: 音声ファイルディレクトリが見つかりません: {audio_dir}")
        print("\n以下の手順でテストデータを準備してください:")
        print("1. mkdir -p test_data/audio")
        print("2. 音声ファイル (.mp3, .wav など) を test_data/audio/ に配置")
        return
    
    if not ground_truth_dir.exists():
        print(f"\n❌ エラー: 正解データディレクトリが見つかりません: {ground_truth_dir}")
        print("\n以下の手順でテストデータを準備してください:")
        print("1. mkdir -p test_data/ground_truth")
        print("2. 正解データファイル (.txt) を test_data/ground_truth/ に配置")
        return
    
    print(f"\n音声ファイルディレクトリ: {audio_dir.absolute()}")
    print(f"正解データディレクトリ: {ground_truth_dir.absolute()}")
    
    # ベンチマークツールの初期化
    print("\nベンチマークツールを初期化中...")
    tool = BenchmarkTool()
    
    # ファイルペアの検出
    print("\nファイルペアを検出中...")
    try:
        pairs = tool.discover_file_pairs(audio_dir, ground_truth_dir)
        
        if not pairs:
            print("\n⚠️  ファイルペアが見つかりませんでした")
            return
        
        print(f"\n✓ {len(pairs)}個のファイルペアを検出しました:")
        for i, (audio_path, gt_path) in enumerate(pairs, 1):
            print(f"  {i}. {audio_path.name} ↔ {gt_path.name}")
        
    except Exception as e:
        print(f"\n❌ ファイルペアの検出中にエラーが発生しました: {e}")
        return
    
    # ========================================
    # 1. 前処理なしでベンチマーク実行
    # ========================================
    print_header("ステップ1: 前処理なしでベンチマーク実行")
    
    try:
        results_without = tool.run_benchmark(
            audio_dir,
            ground_truth_dir,
            enable_preprocessing=False
        )
        
        if not results_without:
            print("\n⚠️  処理に成功した楽曲がありませんでした")
            return
        
        print(f"\n✓ 完了: {len(results_without)}/{len(pairs)}曲が正常に処理されました")
        
    except Exception as e:
        print(f"\n❌ ベンチマークの実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================
    # 2. 前処理ありでベンチマーク実行
    # ========================================
    print_header("ステップ2: 前処理ありでベンチマーク実行")
    
    # 前処理パイプラインの設定
    # 注意: 正解データにタイムスタンプ情報がないため、集約は無効にします
    config = PreprocessingConfig(
        normalization_mode=NormalizationMode.SLASH,
        aggregation_strategy=AggregationStrategy.MOST_FREQUENT,
        aggregation_tolerance=0.1,
        enable_normalization=True,
        enable_aggregation=False  # タイムスタンプ情報がないため無効
    )
    pipeline = PreprocessingPipeline(config)
    tool.set_preprocessing_pipeline(pipeline)
    
    print("\n前処理設定:")
    print(f"  正規化モード: {config.normalization_mode.value}")
    print(f"  集約戦略: {config.aggregation_strategy.value}")
    print(f"  許容誤差: {config.aggregation_tolerance}秒")
    print(f"  正規化: {'有効' if config.enable_normalization else '無効'}")
    print(f"  集約: {'無効' if not config.enable_aggregation else '有効'} (正解データにタイムスタンプ情報がないため)")
    
    try:
        results_with = tool.run_benchmark(
            audio_dir,
            ground_truth_dir,
            enable_preprocessing=True
        )
        
        if not results_with:
            print("\n⚠️  処理に成功した楽曲がありませんでした")
            return
        
        print(f"\n✓ 完了: {len(results_with)}/{len(pairs)}曲が正常に処理されました")
        
    except Exception as e:
        print(f"\n❌ ベンチマークの実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================
    # 3. 結果の比較
    # ========================================
    print_header("ステップ3: 結果の比較")
    
    # 集計統計の比較
    print_metrics_comparison(results_without, results_with, tool)
    
    # 楽曲ごとの比較
    print_song_comparison(results_without, results_with)
    
    # ========================================
    # 4. レポートの生成
    # ========================================
    print_header("レポートの生成")
    
    try:
        # 前処理なしのレポート
        json_without = Path("evaluation_report_without_preprocessing.json")
        md_without = Path("evaluation_report_without_preprocessing.md")
        tool.generate_report(results_without, json_without, format='json')
        tool.generate_report(results_without, md_without, format='markdown')
        print(f"\n✓ 前処理なしのレポートを生成しました:")
        print(f"  - {json_without.absolute()}")
        print(f"  - {md_without.absolute()}")
        
        # 前処理ありのレポート
        json_with = Path("evaluation_report_with_preprocessing.json")
        md_with = Path("evaluation_report_with_preprocessing.md")
        tool.generate_report(results_with, json_with, format='json')
        tool.generate_report(results_with, md_with, format='markdown')
        print(f"\n✓ 前処理ありのレポートを生成しました:")
        print(f"  - {json_with.absolute()}")
        print(f"  - {md_with.absolute()}")
        
    except Exception as e:
        print(f"\n❌ レポートの生成中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ========================================
    # 完了メッセージ
    # ========================================
    print_header("✓ すべての処理が完了しました")
    
    print("\n生成されたファイル:")
    print(f"  前処理なし:")
    print(f"    - {json_without.absolute()}")
    print(f"    - {md_without.absolute()}")
    print(f"  前処理あり:")
    print(f"    - {json_with.absolute()}")
    print(f"    - {md_with.absolute()}")
    print("\nレポートファイルを開いて、詳細な評価結果を確認してください。")


if __name__ == "__main__":
    main()
