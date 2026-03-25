'use client'

import { useState } from 'react'
import type { AnalyzeResponse } from '@/lib/types'

const COLOR_HEX: Record<string, string> = {
  red: '#ff3b5c',
  orange: '#ff8c00',
  yellow: '#fbbf24',
  green: '#22c55e',
  blue: '#3b82f6',
  purple: '#a855f7',
  pink: '#ec4899',
  white: '#e5e7eb',
  gray: '#6b7280',
  black: '#374151',
}

interface ResultsViewProps {
  result: AnalyzeResponse
  originalImageUrl: string
}

function Divider({ label }: { label: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, margin: '4px 0' }}>
      <div style={{ height: 1, flex: 1, background: 'var(--border)' }} />
      <span style={{
        fontFamily: 'var(--font-mono)',
        fontSize: 16,
        color: 'var(--text-muted)',
        letterSpacing: '0.15em',
        textTransform: 'uppercase',
      }}>{label}</span>
      <div style={{ height: 1, flex: 1, background: 'var(--border)' }} />
    </div>
  )
}

function MetricCard({
  value, label, sub, accent, warn
}: { value: string; label: string; sub?: string; accent?: boolean; warn?: boolean }) {
  const color = accent ? 'var(--accent-cyan)' : warn ? '#f59e0b' : 'var(--text-primary)'
  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: `1px solid ${accent ? 'rgba(0,212,255,0.2)' : 'var(--border)'}`,
      borderRadius: 6,
      padding: '18px 20px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {accent && (
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: 1,
          background: 'linear-gradient(90deg, transparent, var(--accent-cyan), transparent)',
        }} />
      )}
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 48, fontWeight: 400, color, lineHeight: 1, letterSpacing: '-0.02em' }}>
        {value}
      </div>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 15, color: 'var(--text-muted)', marginTop: 7, letterSpacing: '0.12em', textTransform: 'uppercase' }}>
        {label}
      </div>
      {sub && (
        <div style={{ fontSize: 16, color: 'var(--text-muted)', marginTop: 4 }}>{sub}</div>
      )}
    </div>
  )
}

export function ResultsView({ result, originalImageUrl }: ResultsViewProps) {
  const [activeTab, setActiveTab] = useState<'detected' | 'original'>('detected')
  const processingSeconds = (result.processing_time_ms / 1000).toFixed(1)
  const colorsCount = result.colors_found.length
  const maxCount = Math.max(...Object.values(result.wire_counts), 1)
  const confidence = result.avg_confidence
  const confidenceLabel = confidence >= 85 ? 'High' : confidence >= 70 ? 'Medium' : 'Low'

  return (
    <div className="animate-slide-in" style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>

      <Divider label="Detection Results" />

      {/* ── TOP ROW: 5 metric cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
        <MetricCard value={String(result.total_wires)} label="Wire Segments" accent />
        <MetricCard value={String(colorsCount)} label="Colors Found" />
        <MetricCard value={`${confidence}%`} label="Avg Confidence" sub={confidenceLabel} warn={confidence < 70} />
        <MetricCard value={`${result.wire_coverage_pct}%`} label="Wire Coverage" />
        <MetricCard value={`${processingSeconds}s`} label="Process Time" />
      </div>

      {/* ── MIDDLE ROW: image comparison (left) + color bars (right) ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16, alignItems: 'start' }}>

        {/* Image panel with tab switcher */}
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 6, overflow: 'hidden' }}>
          {/* Tab bar */}
          <div style={{
            display: 'flex',
            borderBottom: '1px solid var(--border)',
            background: 'var(--bg-elevated)',
          }}>
            {(['detected', 'original'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  background: activeTab === tab ? 'var(--bg-surface)' : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === tab ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                  color: activeTab === tab ? 'var(--text-primary)' : 'var(--text-muted)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 16,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {tab === 'detected' ? 'Detected' : 'Original'}
              </button>
            ))}
          </div>

          {/* Image */}
          <div style={{ position: 'relative' }}>
            <img
              src={activeTab === 'detected'
                ? `data:image/png;base64,${result.annotated_image}`
                : originalImageUrl}
              alt={activeTab === 'detected' ? 'Detected wires' : 'Original image'}
              style={{ width: '100%', height: 'auto', display: 'block' }}
            />
            <div style={{
              position: 'absolute', top: 10, left: 10,
              background: 'rgba(7,8,10,0.75)',
              border: '1px solid var(--border)',
              borderRadius: 3,
              padding: '3px 10px',
              fontFamily: 'var(--font-mono)',
              fontSize: 15,
              color: activeTab === 'detected' ? 'var(--accent-cyan)' : 'var(--text-muted)',
              letterSpacing: '0.1em',
              backdropFilter: 'blur(6px)',
            }}>
              {activeTab === 'detected' ? '▸ SAM SEGMENTED' : '◉ ORIGINAL'}
            </div>
          </div>
        </div>

        {/* Right column: color breakdown + stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          {/* Color distribution */}
          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 6, padding: '18px 20px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 15, color: 'var(--text-muted)', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 16 }}>
              Color Distribution
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {result.colors_found.length === 0 ? (
                <p style={{ fontSize: 17, color: 'var(--text-muted)' }}>No wires detected</p>
              ) : (
                result.colors_found
                  .sort((a, b) => result.wire_counts[b] - result.wire_counts[a])
                  .map((color) => {
                    const count = result.wire_counts[color]
                    const pct = Math.round((count / maxCount) * 100)
                    const hex = COLOR_HEX[color] ?? '#888'
                    return (
                      <div key={color}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 5 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <div style={{
                              width: 10, height: 10, borderRadius: '50%',
                              background: hex,
                              boxShadow: `0 0 6px ${hex}88`,
                              flexShrink: 0,
                            }} />
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 17, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                              {color}
                            </span>
                          </div>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 20, color: 'var(--text-primary)', fontWeight: 500 }}>
                            {count}
                          </span>
                        </div>
                        <div style={{ height: 5, background: 'var(--bg-elevated)', borderRadius: 3, overflow: 'hidden' }}>
                          <div style={{
                            height: '100%',
                            width: `${pct}%`,
                            background: `linear-gradient(90deg, ${hex}99, ${hex})`,
                            borderRadius: 3,
                            transition: 'width 0.9s cubic-bezier(0.16,1,0.3,1)',
                          }} />
                        </div>
                      </div>
                    )
                  })
              )}
            </div>
          </div>

          {/* Segment quality */}
          <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 6, padding: '18px 20px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 15, color: 'var(--text-muted)', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 14 }}>
              Segment Quality
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { label: 'Confidence', value: `${confidence}%`, pct: confidence },
                { label: 'Coverage', value: `${result.wire_coverage_pct}%`, pct: result.wire_coverage_pct },
              ].map(({ label, value, pct }) => (
                <div key={label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 16, color: 'var(--text-muted)' }}>{label}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 17, color: 'var(--text-primary)' }}>{value}</span>
                  </div>
                  <div style={{ height: 4, background: 'var(--bg-elevated)', borderRadius: 2, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${Math.min(pct, 100)}%`,
                      background: pct >= 80 ? 'var(--accent-cyan)' : pct >= 60 ? '#f59e0b' : '#ff3b5c',
                      borderRadius: 2,
                      transition: 'width 1s ease',
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Raw stats */}
          <div style={{
            background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 6,
            padding: '14px 20px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '10px 16px',
          }}>
            {[
              ['SAM Segments', result.segments_analyzed],
              ['Wire Segments', result.total_wires],
              ['Colors', colorsCount],
              ['Time', `${processingSeconds}s`],
            ].map(([label, val]) => (
              <div key={label}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 20, color: 'var(--text-secondary)', lineHeight: 1 }}>
                  {val}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, color: 'var(--text-muted)', marginTop: 3, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                  {label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  )
}
