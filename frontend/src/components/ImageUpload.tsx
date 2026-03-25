'use client'

import { useCallback, useRef, useState } from 'react'

interface ImageUploadProps {
  onFileSelected: (file: File) => void
  isLoading?: boolean
}

export function ImageUpload({ onFileSelected, isLoading = false }: ImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) onFileSelected(file)
    },
    [onFileSelected]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const file = e.dataTransfer.files?.[0]
      if (file) onFileSelected(file)
    },
    [onFileSelected]
  )

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!isLoading && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault()
        inputRef.current?.click()
      }
    },
    [isLoading]
  )

  return (
    <div
      role="button"
      tabIndex={isLoading ? -1 : 0}
      aria-label={isLoading ? 'Analyzing image, please wait' : 'Upload wire image — click or drag and drop'}
      aria-busy={isLoading}
      data-loading={isLoading ? 'true' : undefined}
      className="upload-zone"
      onClick={() => !isLoading && inputRef.current?.click()}
      onKeyDown={handleKeyDown}
      onDrop={handleDrop}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      style={{
        position: 'relative',
        background: isDragging ? 'rgba(0,212,255,0.04)' : 'var(--bg-surface)',
        border: `1px solid ${isDragging ? 'rgba(0,212,255,0.5)' : isLoading ? 'rgba(245,158,11,0.4)' : 'var(--border)'}`,
        borderRadius: 6,
        padding: '40px 24px',
        cursor: isLoading ? 'default' : 'pointer',
        overflow: 'hidden',
        transition: 'border-color 0.2s, background 0.2s',
        animation: isDragging ? 'pulse-border 1.5s ease infinite' : 'none',
      }}
    >
      {/* Corner marks */}
      {['top-left', 'top-right', 'bottom-left', 'bottom-right'].map((pos) => (
        <span
          key={pos}
          style={{
            position: 'absolute',
            width: 12,
            height: 12,
            borderColor: isLoading ? 'rgba(245,158,11,0.6)' : 'var(--accent-cyan)',
            borderStyle: 'solid',
            borderWidth: 0,
            borderTopWidth: pos.startsWith('top') ? 1.5 : 0,
            borderBottomWidth: pos.startsWith('bottom') ? 1.5 : 0,
            borderLeftWidth: pos.endsWith('left') ? 1.5 : 0,
            borderRightWidth: pos.endsWith('right') ? 1.5 : 0,
            top: pos.startsWith('top') ? 8 : 'auto',
            bottom: pos.startsWith('bottom') ? 8 : 'auto',
            left: pos.endsWith('left') ? 8 : 'auto',
            right: pos.endsWith('right') ? 8 : 'auto',
            opacity: 0.7,
          }}
        />
      ))}

      {/* Scan line when loading */}
      {isLoading && (
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            height: 1,
            background: 'linear-gradient(90deg, transparent, rgba(245,158,11,0.6), transparent)',
            animation: 'scanline 1.8s linear infinite',
            top: 0,
          }}
        />
      )}

      <input
        ref={inputRef}
        data-testid="file-input"
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={handleChange}
        style={{ display: 'none' }}
      />

      <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
        {isLoading ? (
          <>
            <div style={{ marginBottom: 12 }}>
              {/* Animated waveform */}
              <svg width="48" height="24" viewBox="0 0 48 24" fill="none" style={{ margin: '0 auto' }}>
                {[0, 1, 2, 3, 4, 5, 6].map((i) => (
                  <rect
                    key={i}
                    x={i * 7}
                    y={12 - (i % 3 === 0 ? 10 : i % 3 === 1 ? 6 : 3)}
                    width={4}
                    height={i % 3 === 0 ? 20 : i % 3 === 1 ? 12 : 6}
                    rx={1}
                    fill="rgba(245,158,11,0.7)"
                    style={{
                      animation: `flicker ${0.8 + i * 0.15}s ease-in-out infinite`,
                      animationDelay: `${i * 0.1}s`,
                    }}
                  />
                ))}
              </svg>
            </div>
            <p
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 16,
                color: '#f59e0b',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
              }}
            >
              Analyzing...
            </p>
            <p style={{ fontSize: 15, color: 'var(--text-muted)', marginTop: 4 }}>
              SAM segmenting wires · please wait
            </p>
          </>
        ) : (
          <>
            <div style={{ marginBottom: 12 }}>
              <svg width="36" height="36" viewBox="0 0 36 36" fill="none" style={{ margin: '0 auto', display: 'block' }}>
                <rect x="0.75" y="0.75" width="34.5" height="34.5" rx="3.25" stroke="var(--border-bright)" strokeWidth="1.5" />
                <path d="M18 11v14M11 18h14" stroke="var(--accent-cyan)" strokeWidth="1.5" strokeLinecap="round" opacity="0.7" />
              </svg>
            </div>
            <p
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 17,
                color: 'var(--text-primary)',
                letterSpacing: '0.05em',
              }}
            >
              Drop image here
            </p>
            <p style={{ fontSize: 16, color: 'var(--text-muted)', marginTop: 4 }}>
              or click to select · PNG, JPEG, WebP
            </p>
          </>
        )}
      </div>
    </div>
  )
}
