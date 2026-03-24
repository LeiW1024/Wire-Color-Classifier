import { AnalyzeResponse, ColorsResponse } from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function getColors(): Promise<ColorsResponse> {
  const response = await fetch(`${API_BASE}/api/colors`)

  if (!response.ok) {
    throw new Error(`Failed to fetch colors: ${response.status}`)
  }

  return response.json()
}
