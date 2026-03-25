interface ColorTableProps {
  wireCounts: Record<string, number>
  totalWires: number
}

export function ColorTable({ wireCounts, totalWires }: ColorTableProps) {
  const entries = Object.entries(wireCounts)

  if (entries.length === 0) {
    return (
      <p style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)', textAlign: 'center', padding: '16px 0' }}>
        No colors detected
      </p>
    )
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'var(--font-mono)', fontSize: 14 }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)' }}>
            <th style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: 12 }}>Color</th>
            <th style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase', fontSize: 12 }}>Count</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([color, count]) => (
            <tr key={color} style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 12px', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{color}</td>
              <td style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-primary)' }}>{count}</td>
            </tr>
          ))}
          <tr>
            <td style={{ padding: '8px 12px', color: 'var(--text-muted)', textTransform: 'uppercase', fontSize: 12, letterSpacing: '0.1em' }}>Total</td>
            <td style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--accent-cyan)', fontWeight: 500 }}>{totalWires}</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}
