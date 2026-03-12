"""
実際の楽曲データでベンチマークを実行するスクリプト

使用方法:
1. test_data/audio/ に音声ファイルを配置
2. test_data/ground_truth/ に正解データファイルを配置
3. このスクリプトを実行: python examples/real_song_benchmark.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import BenchmarkTool


def main():
    """実際の楽曲データでベンチマークを実行"""
    
    print("=" * 70)
    print("評価システム - 実際の楽曲データでのベンチマーク")
    print("=" * 70)
    
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
        print("\n正解データのフォーマット例:")
        print("  [D][A][Bm7][G]  (コード進行のみ)")
        print("  または")
        print("  涙[D]があふれ[A]る  (歌詞+コード)")
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
            print("\n確認事項:")
            print("1. 音声ファイルと正解データファイルの名前が一致しているか")
            print("   例: song1.mp3 → song1.txt")
            print("2. ファイルが正しいディレクトリに配置されているか")
            return
        
        print(f"\n✓ {len(pairs)}個のファイルペアを検出しました:")
        for i, (audio_path, gt_path) in enumerate(pairs, 1):
            print(f"  {i}. {audio_path.name} ↔ {gt_path.name}")
        
    except Exception as e:
        print(f"\n❌ ファイルペアの検出中にエラーが発生しました: {e}")
        return
    
    # ベンチマークの実行
    print(f"\n{'=' * 70}")
    print("ベンチマークを実行中...")
    print(f"{'=' * 70}\n")
    
    try:
        results = tool.run_benchmark(audio_dir, ground_truth_dir)
        
        if not results:
            print("\n⚠️  処理に成功した楽曲がありませんでした")
            print("ログを確認して、エラーの原因を特定してください")
            return
        
        print(f"\n{'=' * 70}")
        print(f"✓ ベンチマーク完了: {len(results)}/{len(pairs)}曲が正常に処理されました")
        print(f"{'=' * 70}")
        
    except Exception as e:
        print(f"\n❌ ベンチマークの実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 結果のサマリー表示
    print("\n" + "=" * 70)
    print("評価結果サマリー")
    print("=" * 70)
    
    # 集計統計の計算
    aggregates = tool.aggregate_metrics(results)
    
    print("\n【集計統計】")
    print(f"  処理楽曲数: {len(results)}曲")
    print(f"\n  ルート音精度:")
    print(f"    平均: {aggregates['root_accuracy_mean']:.2%}")
    print(f"    標準偏差: {aggregates['root_accuracy_std']:.3f}")
    print(f"    最小: {aggregates['root_accuracy_min']:.2%}")
    print(f"    最大: {aggregates['root_accuracy_max']:.2%}")
    
    print(f"\n  コード品質精度:")
    print(f"    平均: {aggregates['quality_accuracy_mean']:.2%}")
    print(f"    標準偏差: {aggregates['quality_accuracy_std']:.3f}")
    print(f"    最小: {aggregates['quality_accuracy_min']:.2%}")
    print(f"    最大: {aggregates['quality_accuracy_max']:.2%}")
    
    print(f"\n  DTW距離:")
    print(f"    平均: {aggregates['dtw_distance_mean']:.4f}")
    print(f"    標準偏差: {aggregates['dtw_distance_std']:.4f}")
    print(f"    最小: {aggregates['dtw_distance_min']:.4f}")
    print(f"    最大: {aggregates['dtw_distance_max']:.4f}")
    
    print(f"\n  完全一致率:")
    print(f"    平均: {aggregates['exact_match_rate_mean']:.2%}")
    print(f"    標準偏差: {aggregates['exact_match_rate_std']:.3f}")
    print(f"    最小: {aggregates['exact_match_rate_min']:.2%}")
    print(f"    最大: {aggregates['exact_match_rate_max']:.2%}")
    
    # 楽曲ごとの結果
    print("\n" + "=" * 70)
    print("楽曲ごとの詳細結果")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"\n【{i}. {result.song_name}】")
        print(f"  ルート音精度: {result.metrics.root_accuracy:.2%}")
        print(f"  コード品質精度: {result.metrics.quality_accuracy:.2%}")
        print(f"  DTW距離: {result.metrics.dtw_distance:.4f}")
        print(f"  完全一致率: {result.metrics.exact_match_rate:.2%}")
        print(f"  処理時間: {result.processing_time:.2f}秒")
        print(f"  予測コード数: {len(result.predicted_chords)}個")
        print(f"  正解コード数: {len(result.ground_truth_chords)}個")
    
    # レポートの生成
    print("\n" + "=" * 70)
    print("レポートを生成中...")
    print("=" * 70)
    
    try:
        # JSONレポート
        json_path = Path("evaluation_report.json")
        tool.generate_report(results, json_path, format='json')
        print(f"\n✓ JSONレポートを生成しました: {json_path.absolute()}")
        
        # Markdownレポート
        md_path = Path("evaluation_report.md")
        tool.generate_report(results, md_path, format='markdown')
        print(f"✓ Markdownレポートを生成しました: {md_path.absolute()}")
        
    except Exception as e:
        print(f"\n❌ レポートの生成中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 完了メッセージ
    print("\n" + "=" * 70)
    print("✓ すべての処理が完了しました")
    print("=" * 70)
    print("\n生成されたファイル:")
    print(f"  - {json_path.absolute()}")
    print(f"  - {md_path.absolute()}")
    print("\nレポートファイルを開いて、詳細な評価結果を確認してください。")


if __name__ == "__main__":
    main()
