import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import ChordVisualization from '../src/components/ChordVisualization'

/**
 * Chord Layout Tests
 * 
 * These tests verify that chords are grouped into lines of exactly 16 bars
 * with proper tempo-aware bar calculation.
 * 
 * Requirements: 2.6
 * 
 * Test Strategy:
 * - Test that bar calculation accounts for tempo correctly
 * - Test that chords are grouped into 16-bar lines
 * - Test with different tempos and chord durations
 */

describe('Chord Layout - 16 Bars Per Line', () => {
  describe('Bar Calculation with Tempo (Requirement 2.6)', () => {
    it('should group 32 chords (4 seconds each) into 4 lines at 120 BPM', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 120 // BPM
      
      // At 120 BPM:
      // - 1 beat = 60/120 = 0.5 seconds
      // - 1 bar (4 beats) = 2 seconds
      // - 4 seconds = 2 bars per chord
      // - 32 chords × 2 bars = 64 bars total
      // - Expected: 4 lines of 16 bars each
      
      const chords = []
      for (let i = 0; i < 32; i++) {
        chords.push({
          start_time: i * 4.0,
          end_time: (i + 1) * 4.0,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        })
      }
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      // Find all chord lines
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 4 lines (64 bars / 16 bars per line)
      expect(chordLines.length).toBe(4)
    })

    it('should group chords with varying durations correctly at 120 BPM', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 120
      
      // At 120 BPM: 1 bar = 2 seconds
      // Create 16 chords with alternating durations: 2s, 4s, 2s, 4s, ...
      // 8 chords × 1 bar + 8 chords × 2 bars = 24 bars total
      // Expected: Line 1 has 16 bars, Line 2 has 8 bars
      
      const chords = []
      let time = 0.0
      for (let i = 0; i < 16; i++) {
        const duration = i % 2 === 0 ? 2.0 : 4.0 // Alternate between 1 and 2 bars
        chords.push({
          start_time: time,
          end_time: time + duration,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        })
        time += duration
      }
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 2 lines (24 bars: 16 + 8)
      expect(chordLines.length).toBe(2)
    })

    it('should calculate bars correctly at 60 BPM (slower tempo)', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 60 // BPM
      
      // At 60 BPM:
      // - 1 beat = 60/60 = 1 second
      // - 1 bar (4 beats) = 4 seconds
      // - 4 seconds = 1 bar per chord
      // - 32 chords × 1 bar = 32 bars total
      // - Expected: 2 lines of 16 bars each
      
      const chords = []
      for (let i = 0; i < 32; i++) {
        chords.push({
          start_time: i * 4.0,
          end_time: (i + 1) * 4.0,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        })
      }
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 2 lines (32 bars / 16 bars per line)
      expect(chordLines.length).toBe(2)
    })

    it('should calculate bars correctly at 180 BPM (faster tempo)', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 180 // BPM
      
      // At 180 BPM:
      // - 1 beat = 60/180 = 0.333... seconds
      // - 1 bar (4 beats) = 1.333... seconds
      // - 4 seconds = 3 bars per chord
      // - 32 chords × 3 bars = 96 bars total
      // - With 3 bars per chord, can fit 5 chords per line (15 bars, since 6 would be 18)
      // - 32 chords / 5 chords per line = 6.4 lines → 7 lines
      
      const chords = []
      for (let i = 0; i < 32; i++) {
        chords.push({
          start_time: i * 4.0,
          end_time: (i + 1) * 4.0,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        })
      }
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 7 lines (5 chords × 15 bars per line, except last line with 2 chords)
      expect(chordLines.length).toBe(7)
    })

    it('should use default tempo of 120 BPM when tempo prop is not provided', () => {
      const mockOnChordClick = vi.fn()
      
      // Default tempo is 120 BPM
      // At 120 BPM: 1 bar = 2 seconds
      // 32 chords × 4 seconds = 32 chords × 2 bars = 64 bars
      // Expected: 4 lines
      
      const chords = []
      for (let i = 0; i < 32; i++) {
        chords.push({
          start_time: i * 4.0,
          end_time: (i + 1) * 4.0,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        })
      }
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          // No tempo prop provided - should default to 120
        />
      )
      
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 4 lines (same as 120 BPM test)
      expect(chordLines.length).toBe(4)
    })

    it('should handle edge case with single chord', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 120
      
      const chords = [
        {
          start_time: 0,
          end_time: 2,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        },
      ]
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 1 line
      expect(chordLines.length).toBe(1)
    })

    it('should handle edge case with no chords', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 120
      
      const chords: any[] = []
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 0 lines
      expect(chordLines.length).toBe(0)
    })

    it('should handle chords shorter than 1 bar', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 120
      
      // At 120 BPM: 1 bar = 2 seconds
      // Create 32 chords, each 0.5 seconds (0.25 bars, rounds up to 1 bar)
      // 32 chords × 1 bar = 32 bars
      // Expected: 2 lines
      
      const chords = []
      for (let i = 0; i < 32; i++) {
        chords.push({
          start_time: i * 0.5,
          end_time: (i + 1) * 0.5,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        })
      }
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      const chordLines = container.querySelectorAll('.chord-line')
      
      // Should have 2 lines (32 bars / 16 bars per line)
      expect(chordLines.length).toBe(2)
    })
  })

  describe('Line Number Display', () => {
    it('should display correct line numbers starting from 1', () => {
      const mockOnChordClick = vi.fn()
      const tempo = 120
      
      // Create enough chords for 6 lines
      const chords = []
      for (let i = 0; i < 48; i++) {
        chords.push({
          start_time: i * 4.0,
          end_time: (i + 1) * 4.0,
          root: 'C',
          quality: 'major',
          confidence: 0.9,
        })
      }
      
      const { container } = render(
        <ChordVisualization
          chords={chords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
          tempo={tempo}
        />
      )
      
      const lineNumbers = container.querySelectorAll('.line-number')
      
      // Should have 6 line numbers (96 bars / 16 = 6 lines)
      expect(lineNumbers.length).toBe(6)
      
      // First line should start at bar 1
      expect(lineNumbers[0].textContent).toBe('1')
      
      // Second line should start at bar 17 (1 + 16)
      expect(lineNumbers[1].textContent).toBe('17')
      
      // Third line should start at bar 33 (1 + 16 + 16)
      expect(lineNumbers[2].textContent).toBe('33')
    })
  })
})
