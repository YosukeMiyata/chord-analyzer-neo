#!/usr/bin/env python3
"""
Test script to analyze real audio files and check chord detection results.
This helps verify that major chords are prioritized over maj7 chords.
"""

import sys
from pathlib import Path
from src.audio_engine import AudioProcessingEngine

def analyze_audio_file(audio_path: str):
    """Analyze an audio file and display chord detection results."""
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {audio_path}")
    print(f"{'='*60}\n")
    
    # Initialize audio engine
    engine = AudioProcessingEngine()
    
    # Load the audio file
    if not engine.load_audio_file(Path(audio_path)):
        print(f"Error: Failed to load audio file")
        return False
    
    # Analyze the audio file
    try:
        result = engine.analyze_audio()
        
        # Display results
        print(f"Total chords detected: {len(result.chord_progression)}")
        print(f"\nChord progression:")
        print(f"{'Time':<12} {'Chord':<10} {'Confidence':<12}")
        print("-" * 40)
        
        for chord in result.chord_progression:
            time_str = f"{chord.start_time:.1f}-{chord.end_time:.1f}s"
            chord_name = str(chord)
            confidence = f"{chord.confidence:.2%}"
            print(f"{time_str:<12} {chord_name:<10} {confidence:<12}")
        
        # Count chord types
        print(f"\n{'='*60}")
        print("Chord type statistics:")
        print(f"{'='*60}")
        
        chord_types = {}
        for chord in result.chord_progression:
            chord_name = str(chord)
            chord_types[chord_name] = chord_types.get(chord_name, 0) + 1
        
        # Sort by frequency
        sorted_chords = sorted(chord_types.items(), key=lambda x: x[1], reverse=True)
        
        for chord_name, count in sorted_chords:
            print(f"{chord_name:<15} : {count:>3} occurrences")
        
        # Check for major vs maj7
        print(f"\n{'='*60}")
        print("Major chord analysis:")
        print(f"{'='*60}")
        
        major_count = 0
        maj7_count = 0
        dominant7_count = 0
        
        for chord in result.chord_progression:
            chord_str = str(chord)
            if 'maj7' in chord_str:
                maj7_count += 1
            elif chord_str[-1].isdigit() and '7' in chord_str:
                dominant7_count += 1
            elif 'maj' in chord_str or (not any(x in chord_str for x in ['m', '7', 'sus', 'dim', 'aug'])):
                major_count += 1
        
        print(f"Simple major chords (C, D, E, etc.): {major_count}")
        print(f"Major 7th chords (Cmaj7, etc.):      {maj7_count}")
        print(f"Dominant 7th chords (C7, etc.):      {dominant7_count}")
        
        if major_count > maj7_count:
            print("\n✓ Major chords are being prioritized over maj7 chords")
        elif maj7_count > major_count:
            print("\n⚠ Warning: More maj7 chords than simple major chords detected")
        else:
            print("\n- Equal number of major and maj7 chords")
        
        # Average confidence
        avg_confidence = sum(c.confidence for c in result.chord_progression) / len(result.chord_progression)
        print(f"\nAverage confidence: {avg_confidence:.2%}")
        
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main function to run audio analysis."""
    
    if len(sys.argv) < 2:
        print("Usage: python test_real_audio.py <audio_file_path>")
        print("\nExample:")
        print("  python test_real_audio.py /path/to/song.mp3")
        print("  python test_real_audio.py /path/to/song.wav")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    # Check if file exists
    if not Path(audio_path).exists():
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)
    
    # Analyze the file
    success = analyze_audio_file(audio_path)
    
    if success:
        print(f"\n{'='*60}")
        print("Analysis complete!")
        print(f"{'='*60}\n")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
