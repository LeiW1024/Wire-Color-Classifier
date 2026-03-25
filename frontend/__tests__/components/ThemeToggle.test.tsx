import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeToggle } from '@/components/ThemeToggle'

const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  }),
})

beforeEach(() => {
  localStorageMock.clear()
  document.documentElement.removeAttribute('data-theme')
})

describe('ThemeToggle', () => {
  test('shows "☀ LIGHT" label when in dark mode', () => {
    render(<ThemeToggle />)
    expect(screen.getByText(/☀ LIGHT/)).toBeInTheDocument()
  })

  test('shows "🌙 DARK" label after switching to light mode', () => {
    render(<ThemeToggle />)
    fireEvent.click(screen.getByRole('button'))
    expect(screen.getByText(/🌙 DARK/)).toBeInTheDocument()
  })

  test('sets data-theme="light" on html element when switched to light', () => {
    render(<ThemeToggle />)
    fireEvent.click(screen.getByRole('button'))
    expect(document.documentElement.dataset.theme).toBe('light')
  })

  test('persists theme preference to localStorage', () => {
    render(<ThemeToggle />)
    fireEvent.click(screen.getByRole('button'))
    expect(localStorageMock.getItem('theme')).toBe('light')
  })

  test('toggles back to dark mode on second click', () => {
    render(<ThemeToggle />)
    const btn = screen.getByRole('button')
    fireEvent.click(btn)
    fireEvent.click(btn)
    expect(screen.getByText(/☀ LIGHT/)).toBeInTheDocument()
    expect(document.documentElement.dataset.theme).toBe('dark')
  })
})
