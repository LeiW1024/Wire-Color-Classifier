interface ColorTableProps {
  wireCounts: Record<string, number>
  totalWires: number
}

export function ColorTable({ wireCounts, totalWires }: ColorTableProps) {
  const entries = Object.entries(wireCounts)

  if (entries.length === 0) {
    return <p className="text-gray-500 text-center py-4">No colors detected</p>
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left font-medium">Color</th>
            <th className="px-4 py-2 text-right font-medium">Count</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([color, count]) => (
            <tr key={color} className="border-t border-gray-100">
              <td className="px-4 py-2">{color}</td>
              <td className="px-4 py-2 text-right">{count}</td>
            </tr>
          ))}
          <tr className="border-t-2 border-gray-300 font-bold">
            <td className="px-4 py-2">Total</td>
            <td className="px-4 py-2 text-right">{totalWires}</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}
