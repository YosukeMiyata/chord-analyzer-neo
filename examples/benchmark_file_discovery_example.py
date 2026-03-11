"""Example demonstrating BenchmarkTool file discovery functionality.

This example shows how to:
1. Create test directories with audio and ground truth files
2. Use BenchmarkTool to discover and match file pairs
3. Handle missing pairs with warning logs
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile
import logging
from src.evaluation import BenchmarkTool

# Configure logging to see warnings
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """Demonstrate BenchmarkTool file discovery."""
    
    # Create temporary directories for demonstration
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create audio and ground truth directories
        audio_dir = tmp_path / "audio"
        gt_dir = tmp_path / "ground_truth"
        audio_dir.mkdir()
        gt_dir.mkdir()
        
        print("=" * 60)
        print("BenchmarkTool File Discovery Example")
        print("=" * 60)
        
        # Example 1: Perfect matching
        print("\n1. Perfect matching - all files have pairs:")
        print("-" * 60)
        
        # Create matching files
        (audio_dir / "song1.mp3").touch()
        (audio_dir / "song2.wav").touch()
        (audio_dir / "song3.flac").touch()
        
        (gt_dir / "song1.txt").touch()
        (gt_dir / "song2.txt").touch()
        (gt_dir / "song3.txt").touch()
        
        tool = BenchmarkTool()
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        print(f"Found {len(pairs)} matching pairs:")
        for audio, gt in sorted(pairs, key=lambda x: x[0].stem):
            print(f"  - {audio.name} <-> {gt.name}")
        
        # Clean up for next example
        for file in audio_dir.iterdir():
            file.unlink()
        for file in gt_dir.iterdir():
            file.unlink()
        
        # Example 2: Missing ground truth files
        print("\n2. Missing ground truth files:")
        print("-" * 60)
        
        (audio_dir / "song1.mp3").touch()
        (audio_dir / "song2.wav").touch()
        (audio_dir / "song3.flac").touch()
        
        (gt_dir / "song1.txt").touch()
        # song2 and song3 ground truth files are missing
        
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        print(f"Found {len(pairs)} matching pairs:")
        for audio, gt in sorted(pairs, key=lambda x: x[0].stem):
            print(f"  - {audio.name} <-> {gt.name}")
        print("(Check warnings above for missing ground truth files)")
        
        # Clean up for next example
        for file in audio_dir.iterdir():
            file.unlink()
        for file in gt_dir.iterdir():
            file.unlink()
        
        # Example 3: Multiple audio formats
        print("\n3. Multiple audio formats:")
        print("-" * 60)
        
        audio_formats = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"]
        for i, ext in enumerate(audio_formats):
            (audio_dir / f"song{i}{ext}").touch()
            (gt_dir / f"song{i}.txt").touch()
        
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        print(f"Found {len(pairs)} matching pairs:")
        for audio, gt in sorted(pairs, key=lambda x: x[0].stem):
            print(f"  - {audio.name} <-> {gt.name}")
        
        # Clean up for next example
        for file in audio_dir.iterdir():
            file.unlink()
        for file in gt_dir.iterdir():
            file.unlink()
        
        # Example 4: Non-audio files are ignored
        print("\n4. Non-audio files are ignored:")
        print("-" * 60)
        
        (audio_dir / "song1.mp3").touch()
        (audio_dir / "readme.txt").touch()
        (audio_dir / "metadata.json").touch()
        (audio_dir / "image.jpg").touch()
        
        (gt_dir / "song1.txt").touch()
        
        pairs = tool.discover_file_pairs(audio_dir, gt_dir)
        
        print(f"Found {len(pairs)} matching pairs (non-audio files ignored):")
        for audio, gt in sorted(pairs, key=lambda x: x[0].stem):
            print(f"  - {audio.name} <-> {gt.name}")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()
