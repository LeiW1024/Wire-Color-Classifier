'use client'

import { useState, useCallback } from 'react'
import { ImageUpload } from '@/components/ImageUpload'
import { ResultsView } from '@/components/ResultsView'
import { ThemeToggle } from '@/components/ThemeToggle'
import { analyzeImage } from '@/lib/api'
import type { AnalyzeResponse } from '@/lib/types'

export default function Home() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [originalImage, setOriginalImage] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelected = useCallback(async (file: File) => {
    setIsLoading(true)
    setError(null)
    setResult(null)

    // Create a local URL for the original image preview
    const objUrl = URL.createObjectURL(file)
    setOriginalImage(objUrl)

    try {
      const response = await analyzeImage(file)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setIsLoading(false)
    }
  }, [])

  return (
    <div style={{ position: 'relative', minHeight: '100vh', zIndex: 1 }}>
      {/* Skip to main content — keyboard accessibility */}
      <a href="#main-content" className="skip-link">Skip to main content</a>

      {/* Header */}
      <header style={{
        borderBottom: '1px solid var(--border)',
        background: 'var(--bg-surface)',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}>
        <div style={{
          maxWidth: 1100,
          margin: '0 auto',
          padding: '0 24px',
          height: 52,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: isLoading ? '#f59e0b' : result ? 'var(--accent-cyan)' : '#2e3440',
              boxShadow: isLoading ? '0 0 8px #f59e0b' : result ? '0 0 8px rgba(0,212,255,0.6)' : 'none',
              transition: 'all 0.3s ease',
            }} />
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 20,
              color: 'var(--text-secondary)',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
            }}>
              Wire Color Classifier
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 15, color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
              SAM · v2.0
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 15, color: 'var(--text-muted)' }}>|</span>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main id="main-content" style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 24px', display: 'flex', flexDirection: 'column', gap: 32 }}>
        {/* Title */}
        <div style={{ borderLeft: '2px solid var(--accent-cyan)', paddingLeft: 20 }}>
          <h1 style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'clamp(26px, 3vw, 36px)',
            fontWeight: 400,
            color: 'var(--text-primary)',
            letterSpacing: '-0.01em',
            lineHeight: 1.2,
          }}>
            Industrial Wire<br />
            <span style={{ color: 'var(--accent-cyan)' }}>Color Analysis</span>
          </h1>
          <p style={{
            fontSize: 20,
            color: 'var(--text-muted)',
            marginTop: 8,
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.04em',
          }}>
            SAM segmentation → HSV color classification
          </p>
        </div>

        {/* Upload */}
        <ImageUpload onFileSelected={handleFileSelected} isLoading={isLoading} />

        {/* Error */}
        {error && (
          <div
            role="alert"
            aria-live="polite"
            style={{
              background: 'rgba(255,59,92,0.08)',
              border: '1px solid rgba(255,59,92,0.3)',
              borderRadius: 4,
              padding: '14px 18px',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
            }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 15, color: 'var(--accent-red)', letterSpacing: '0.1em' }}>ERR</span>
            <span style={{ fontSize: 20, color: '#ff8fa3' }}>{error}</span>
          </div>
        )}

        {/* Results */}
        {result && originalImage && (
          <ResultsView result={result} originalImageUrl={originalImage} />
        )}
      </main>
    </div>
  )
}
