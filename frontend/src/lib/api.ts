import { AnalyzeResponse, ColorsResponse } from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 120000) // 2 min timeout for SAM model load

  try {
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(`Analysis failed: ${response.status} ${text}`)
    }

    return response.json()
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error('Request timed out. The model may still be loading — please try again.')
    }
    throw err
  } finally {
    clearTimeout(timeout)
  }
}

export async function getColors(): Promise<ColorsResponse> {
  const response = await fetch(`${API_BASE}/api/colors`)

  if (!response.ok) {
    throw new Error(`Failed to fetch colors: ${response.status}`)
  }

  return response.json()
}
