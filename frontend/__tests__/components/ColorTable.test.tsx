import { render, screen } from '@testing-library/react'
import { ColorTable } from '@/components/ColorTable'

describe('ColorTable', () => {
  test('renders all detected colors with counts', () => {
    const wireCounts = { red: 3, blue: 5, green: 2 }
    render(<ColorTable wireCounts={wireCounts} totalWires={10} />)

    expect(screen.getByText('red')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
    expect(screen.getByText('blue')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  test('shows message when no colors detected', () => {
    render(<ColorTable wireCounts={{}} totalWires={0} />)
    expect(screen.getByText(/no colors detected/i)).toBeInTheDocument()
  })
})
