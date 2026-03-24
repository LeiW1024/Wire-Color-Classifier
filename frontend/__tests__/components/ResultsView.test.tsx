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
  }

  test('renders annotated image', () => {
    render(<ResultsView result={mockResult} />)
    const img = screen.getByRole('img')
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', expect.stringContaining('data:image/png;base64'))
  })

  test('renders color table', () => {
    render(<ResultsView result={mockResult} />)
    expect(screen.getByText('red')).toBeInTheDocument()
    expect(screen.getByText('blue')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument()
  })
})
