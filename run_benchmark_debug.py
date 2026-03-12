"""
デバッグ用ベンチマークスクリプト - 詳細なログ出力付き
"""

import sys
import logging
from pathlib import Path

# ログ設定を最初に行う
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.evaluation import BenchmarkTool


def main():
    """実際の楽曲データでベンチマークを実行（デバッグモード）"""
    
    print("=" * 70)
    print("評価システム - デバッグモード")
    print("=" * 70)
    
    # ディレクトリパスの設定
    audio_dir = Path("test_data/audio")
    ground_truth_dir = Path("test_data/ground_truth")
    
    print(f"\n音声ファイルディレクトリ: {audio_dir.absolute()}")
    print(f"正解データディレクトリ: {ground_truth_dir.absolute()}")
    
    # ベンチマークツールの初期化
    print("\nベンチマークツールを初期化中...")
    tool = BenchmarkTool()
    
    # ファイルペアの検出
    print("\nファイルペアを検出中...")
    pairs = tool.discover_file_pairs(audio_dir, ground_truth_dir)
    
    print(f"\n✓ {len(pairs)}個のファイルペアを検出しました:")
    for i, (audio_path, gt_path) in enumerate(pairs, 1):
        print(f"  {i}. {audio_path.name} ↔ {gt_path.name}")
    
    # 1曲だけ処理してみる
    if pairs:
        print(f"\n{'=' * 70}")
        print("最初の1曲を処理中...")
        print(f"{'=' * 70}\n")
        
        audio_path, gt_path = pairs[0]
        
        try:
            result = tool.process_single_song(audio_path, gt_path)
            
            print(f"\n{'=' * 70}")
            print("✓ 処理完了")
            print(f"{'=' * 70}")
            print(f"\n楽曲名: {result.song_name}")
            print(f"ルート音精度: {result.metrics.root_accuracy:.2%}")
            print(f"コード品質精度: {result.metrics.quality_accuracy:.2%}")
            print(f"DTW距離: {result.metrics.dtw_distance:.4f}")
            print(f"完全一致率: {result.metrics.exact_match_rate:.2%}")
            print(f"処理時間: {result.processing_time:.2f}秒")
            print(f"\n予測コード数: {len(result.predicted_chords)}個")
            print(f"正解コード数: {len(result.ground_truth_chords)}個")
            
            print(f"\n予測コード（最初の10個）:")
            print(" ".join(result.predicted_chords[:10]))
            
            print(f"\n正解コード（最初の10個）:")
            print(" ".join(result.ground_truth_chords[:10]))
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
