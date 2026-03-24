'use client'

import { useState } from 'react'
import { ImageUpload } from '@/components/ImageUpload'
import { ResultsView } from '@/components/ResultsView'
import { analyzeImage } from '@/lib/api'
import type { AnalyzeResponse } from '@/lib/types'

export default function Home() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleFileSelected(file: File) {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await analyzeImage(file)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="max-w-4xl mx-auto p-6 space-y-8">
      <h1 className="text-3xl font-bold">Wire Color Classifier</h1>
      <p className="text-gray-600">
        Upload an image of colored wires to detect and count each color.
      </p>

      <ImageUpload onFileSelected={handleFileSelected} isLoading={isLoading} />

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {result && <ResultsView result={result} />}
    </main>
  )
}
