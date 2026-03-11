import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ChordVisualization from '../src/components/ChordVisualization'

/**
 * UI Interaction Preservation Tests
 * 
 * These tests verify that UI interactions remain unchanged after bugfixes.
 * They capture the baseline behavior on UNFIXED code and ensure no regressions.
 * 
 * Requirements: 3.2, 3.3, 3.4
 * 
 * Test Strategy:
 * - Test click handlers on chord segments
 * - Test playback highlighting based on current position
 * - Verify chord details are displayed correctly
 * - Verify current chord highlighting works correctly
 */

describe('UI Interaction Preservation', () => {
  const mockChords = [
    {
      start_time: 0,
      end_time: 2,
      root: 'C',
      quality: 'major',
      confidence: 0.85,
    },
    {
      start_time: 2,
      end_time: 4,
      root: 'G',
      quality: 'major',
      confidence: 0.90,
    },
    {
      start_time: 4,
      end_time: 6,
      root: 'Am',
      quality: 'minor',
      confidence: 0.75,
    },
    {
      start_time: 6,
      end_time: 8,
      root: 'F',
      quality: 'major',
      confidence: 0.65, // Low confidence
    },
  ]

  describe('Chord Click Handler Preservation (Requirement 3.3)', () => {
    it('should call onChordClick with correct chord when chord segment is clicked', () => {
      const mockOnChordClick = vi.fn()
      
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      // Find the first chord button (C major)
      const chordButtons = screen.getAllByRole('button')
      const firstChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      
      expect(firstChordButton).toBeDefined()
      
      // Click the chord
      fireEvent.click(firstChordButton!)
      
      // Verify onChordClick was called with the correct chord
      expect(mockOnChordClick).toHaveBeenCalledTimes(1)
      expect(mockOnChordClick).toHaveBeenCalledWith(mockChords[0])
    })

    it('should display chord details in title attribute', () => {
      const mockOnChordClick = vi.fn()
      
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      // Find the first chord button
      const chordButtons = screen.getAllByRole('button')
      const firstChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      
      expect(firstChordButton).toBeDefined()
      
      // Verify title contains chord name and confidence
      const title = firstChordButton!.getAttribute('title')
      expect(title).toContain('Cmajor')
      expect(title).toContain('85%') // 0.85 * 100 = 85%
    })

    it('should call onChordClick for each different chord when clicked', () => {
      const mockOnChordClick = vi.fn()
      
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      
      // Click the second chord (G major)
      const secondChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Gmajor')
      )
      fireEvent.click(secondChordButton!)
      
      expect(mockOnChordClick).toHaveBeenCalledWith(mockChords[1])
      
      // Click the third chord (Am minor)
      const thirdChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Amminor')
      )
      fireEvent.click(thirdChordButton!)
      
      expect(mockOnChordClick).toHaveBeenCalledWith(mockChords[2])
      
      expect(mockOnChordClick).toHaveBeenCalledTimes(2)
    })
  })

  describe('Playback Highlighting Preservation (Requirement 3.4)', () => {
    it('should highlight current chord when position is within chord time range', () => {
      const mockOnChordClick = vi.fn()
      
      // Current position at 1 second (within first chord: 0-2s)
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={1}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const firstChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      
      // Verify the first chord has 'current' class
      expect(firstChordButton).toBeDefined()
      expect(firstChordButton!.className).toContain('current')
    })

    it('should not highlight chord when position is outside chord time range', () => {
      const mockOnChordClick = vi.fn()
      
      // Current position at 1 second (first chord is 0-2s, second is 2-4s)
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={1}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const secondChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Gmajor')
      )
      
      // Verify the second chord does NOT have 'current' class
      expect(secondChordButton).toBeDefined()
      expect(secondChordButton!.className).not.toContain('current')
    })

    it('should update highlighting when currentPosition changes', () => {
      const mockOnChordClick = vi.fn()
      
      // Initial position at 1 second (first chord)
      const { rerender } = render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={1}
          onChordClick={mockOnChordClick}
        />
      )

      let chordButtons = screen.getAllByRole('button')
      let firstChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      let secondChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Gmajor')
      )
      
      // First chord should be highlighted
      expect(firstChordButton!.className).toContain('current')
      expect(secondChordButton!.className).not.toContain('current')
      
      // Update position to 3 seconds (second chord: 2-4s)
      rerender(
        <ChordVisualization
          chords={mockChords}
          currentPosition={3}
          onChordClick={mockOnChordClick}
        />
      )

      chordButtons = screen.getAllByRole('button')
      firstChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      secondChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Gmajor')
      )
      
      // Second chord should now be highlighted
      expect(firstChordButton!.className).not.toContain('current')
      expect(secondChordButton!.className).toContain('current')
    })

    it('should highlight chord at exact start time', () => {
      const mockOnChordClick = vi.fn()
      
      // Position exactly at second chord start time (2s)
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={2}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const secondChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Gmajor')
      )
      
      // Second chord should be highlighted (start_time <= currentPosition < end_time)
      expect(secondChordButton!.className).toContain('current')
    })

    it('should not highlight chord at exact end time', () => {
      const mockOnChordClick = vi.fn()
      
      // Position exactly at first chord end time (2s)
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={2}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const firstChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      
      // First chord should NOT be highlighted (end_time is exclusive)
      expect(firstChordButton!.className).not.toContain('current')
    })
  })

  describe('Low Confidence Visual Distinction Preservation (Requirement 3.2)', () => {
    it('should apply low-confidence class to chords with confidence < 70%', () => {
      const mockOnChordClick = vi.fn()
      
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      
      // Fourth chord has confidence 0.65 (< 0.7)
      const lowConfidenceButton = chordButtons.find(btn => 
        btn.textContent?.includes('Fmajor')
      )
      
      expect(lowConfidenceButton).toBeDefined()
      expect(lowConfidenceButton!.className).toContain('low-confidence')
    })

    it('should not apply low-confidence class to chords with confidence >= 70%', () => {
      const mockOnChordClick = vi.fn()
      
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      
      // First chord has confidence 0.85 (>= 0.7)
      const highConfidenceButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      
      expect(highConfidenceButton).toBeDefined()
      expect(highConfidenceButton!.className).not.toContain('low-confidence')
    })

    it('should apply low-confidence class to chord with exactly 69% confidence', () => {
      const mockOnChordClick = vi.fn()
      const chordsWithBoundary = [
        {
          start_time: 0,
          end_time: 2,
          root: 'C',
          quality: 'major',
          confidence: 0.69, // Just below threshold
        },
      ]
      
      render(
        <ChordVisualization
          chords={chordsWithBoundary}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const chordButton = chordButtons[0]
      
      expect(chordButton.className).toContain('low-confidence')
    })

    it('should not apply low-confidence class to chord with exactly 70% confidence', () => {
      const mockOnChordClick = vi.fn()
      const chordsWithBoundary = [
        {
          start_time: 0,
          end_time: 2,
          root: 'C',
          quality: 'major',
          confidence: 0.70, // Exactly at threshold
        },
      ]
      
      render(
        <ChordVisualization
          chords={chordsWithBoundary}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const chordButton = chordButtons[0]
      
      expect(chordButton.className).not.toContain('low-confidence')
    })
  })

  describe('Chord Formatting Preservation', () => {
    it('should format chord with extensions correctly', () => {
      const mockOnChordClick = vi.fn()
      const chordsWithExtensions = [
        {
          start_time: 0,
          end_time: 2,
          root: 'C',
          quality: 'major',
          extensions: ['9', '11'],
          confidence: 0.85,
        },
      ]
      
      render(
        <ChordVisualization
          chords={chordsWithExtensions}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const chordButton = chordButtons[0]
      
      // Should display as "Cmajor(9,11)"
      expect(chordButton.textContent).toContain('Cmajor(9,11)')
    })

    it('should format slash chord with bass note correctly', () => {
      const mockOnChordClick = vi.fn()
      const slashChords = [
        {
          start_time: 0,
          end_time: 2,
          root: 'A',
          quality: 'major',
          bass_note: 'G',
          confidence: 0.85,
        },
      ]
      
      render(
        <ChordVisualization
          chords={slashChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const chordButton = chordButtons[0]
      
      // Should display as "Amajor/G"
      expect(chordButton.textContent).toContain('Amajor/G')
    })

    it('should format chord with both extensions and bass note correctly', () => {
      const mockOnChordClick = vi.fn()
      const complexChords = [
        {
          start_time: 0,
          end_time: 2,
          root: 'C',
          quality: 'major',
          extensions: ['7', '9'],
          bass_note: 'E',
          confidence: 0.85,
        },
      ]
      
      render(
        <ChordVisualization
          chords={complexChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const chordButton = chordButtons[0]
      
      // Should display as "Cmajor(7,9)/E"
      expect(chordButton.textContent).toContain('Cmajor(7,9)/E')
    })
  })

  describe('Time Display Preservation', () => {
    it('should display chord start time with one decimal place', () => {
      const mockOnChordClick = vi.fn()
      
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const firstChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Cmajor')
      )
      
      // Should display "0.0s"
      expect(firstChordButton!.textContent).toContain('0.0s')
    })

    it('should display chord start time correctly for non-zero times', () => {
      const mockOnChordClick = vi.fn()
      
      render(
        <ChordVisualization
          chords={mockChords}
          currentPosition={0}
          onChordClick={mockOnChordClick}
        />
      )

      const chordButtons = screen.getAllByRole('button')
      const secondChordButton = chordButtons.find(btn => 
        btn.textContent?.includes('Gmajor')
      )
      
      // Should display "2.0s"
      expect(secondChordButton!.textContent).toContain('2.0s')
    })
  })
})
