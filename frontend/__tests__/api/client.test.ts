import { analyzeImage, getColors } from '@/lib/api'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('API Client', () => {
  afterEach(() => {
    mockFetch.mockReset()
  })

  test('analyzeImage sends file as FormData', async () => {
    const mockResponse = {
      colors_found: ['red'],
      wire_counts: { red: 1 },
      total_wires: 1,
      bounding_boxes: [],
      annotated_image: 'base64data',
    }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const file = new File(['test'], 'test.png', { type: 'image/png' })
    const result = await analyzeImage(file)

    expect(mockFetch).toHaveBeenCalledTimes(1)
    const [url, options] = mockFetch.mock.calls[0]
    expect(url).toContain('/api/analyze')
    expect(options.method).toBe('POST')
    expect(options.body).toBeInstanceOf(FormData)
    expect(result).toEqual(mockResponse)
  })

  test('analyzeImage throws on server error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    })

    const file = new File(['test'], 'test.png', { type: 'image/png' })
    await expect(analyzeImage(file)).rejects.toThrow()
  })

  test('getColors returns color list', async () => {
    const mockResponse = { colors: [] }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    })

    const result = await getColors()
    expect(result).toEqual(mockResponse)
  })
})
