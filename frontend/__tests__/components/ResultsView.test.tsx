import { render, screen } from '@testing-library/react'
import { ResultsView } from '@/components/ResultsView'
import type { AnalyzeResponse } from '@/lib/types'

describe('ResultsView', () => {
  const mockResult: AnalyzeResponse = {
    colors_found: ['red', 'blue'],
    wire_counts: { red: 3, blue: 5 },
    total_wires: 8,
    bounding_boxes: [],
    annotated_image: 'dGVzdA==',
    processing_time_ms: 5000,
    segments_analyzed: 42,
    avg_confidence: 87.5,
    wire_coverage_pct: 12.3,
  }

  test('renders annotated image', () => {
    render(<ResultsView result={mockResult} originalImageUrl="blob:test" />)
    const imgs = screen.getAllByRole('img')
    expect(imgs.length).toBeGreaterThan(0)
    expect(imgs[0]).toHaveAttribute('src', expect.stringContaining('data:image/png;base64'))
  })

  test('renders color names', () => {
    render(<ResultsView result={mockResult} originalImageUrl="blob:test" />)
    expect(screen.getByText('red')).toBeInTheDocument()
    expect(screen.getByText('blue')).toBeInTheDocument()
  })

  test('renders total wire count', () => {
    render(<ResultsView result={mockResult} originalImageUrl="blob:test" />)
    expect(screen.getByText('8')).toBeInTheDocument()
  })
})
