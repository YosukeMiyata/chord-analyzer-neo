"""Demo script for markdown report generation.

This script demonstrates how to generate a markdown evaluation report
from benchmark results.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.models import BenchmarkResult, EvaluationMetrics
from src.evaluation.benchmark import BenchmarkTool


def main():
    """Generate a sample markdown report."""
    
    # Create sample benchmark results
    results = [
        BenchmarkResult(
            song_name="Yesterday",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.95,
                root_accuracy=0.98,
                quality_accuracy=0.96,
                dtw_distance=0.05,
                exact_match_rate=0.92
            ),
            predicted_chords=["F", "Em7", "A7", "Dm", "Bb", "C7", "F"],
            ground_truth_chords=["F", "Em7", "A7", "Dm", "Bb", "C7", "F"],
            processing_time=2.3
        ),
        BenchmarkResult(
            song_name="Let It Be",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.88,
                root_accuracy=0.92,
                quality_accuracy=0.90,
                dtw_distance=0.12,
                exact_match_rate=0.85
            ),
            predicted_chords=["C", "G", "Am", "F", "C", "G", "F", "C"],
            ground_truth_chords=["C", "G", "Am", "F", "C", "G", "F", "C"],
            processing_time=3.1
        ),
        BenchmarkResult(
            song_name="Hey Jude",
            metrics=EvaluationMetrics(
                sequence_accuracy=0.82,
                root_accuracy=0.89,
                quality_accuracy=0.85,
                dtw_distance=0.18,
                exact_match_rate=0.78
            ),
            predicted_chords=["F", "C", "C7", "F", "Bb", "F", "C7", "F"],
            ground_truth_chords=["F", "C", "C7", "F", "Bb", "F", "C7", "F"],
            processing_time=4.2
        )
    ]
    
    # Create benchmark tool
    tool = BenchmarkTool()
    
    # Generate markdown report
    output_path = Path("evaluation_report.md")
    tool.generate_report(results, output_path, format='markdown')
    
    print(f"✓ Markdown report generated: {output_path}")
    print(f"✓ Total songs processed: {len(results)}")
    print(f"\nReport preview:")
    print("-" * 60)
    
    # Display first few lines of the report
    with open(output_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[:20]:
            print(line.rstrip())
    
    print("-" * 60)
    print(f"\nFull report saved to: {output_path.absolute()}")


if __name__ == "__main__":
    main()
