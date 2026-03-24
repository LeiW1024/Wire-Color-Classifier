import { render, screen, fireEvent } from '@testing-library/react'
import { ImageUpload } from '@/components/ImageUpload'

describe('ImageUpload', () => {
  test('renders upload area', () => {
    render(<ImageUpload onFileSelected={jest.fn()} />)
    expect(screen.getByText(/upload/i)).toBeInTheDocument()
  })

  test('calls onFileSelected with valid image', () => {
    const onFileSelected = jest.fn()
    render(<ImageUpload onFileSelected={onFileSelected} />)

    const input = screen.getByTestId('file-input')
    const file = new File(['test'], 'test.png', { type: 'image/png' })
    fireEvent.change(input, { target: { files: [file] } })

    expect(onFileSelected).toHaveBeenCalledWith(file)
  })

  test('shows loading state when isLoading is true', () => {
    render(<ImageUpload onFileSelected={jest.fn()} isLoading={true} />)
    expect(screen.getByText(/processing/i)).toBeInTheDocument()
  })
})
