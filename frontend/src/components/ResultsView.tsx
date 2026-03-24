import type { AnalyzeResponse } from '@/lib/types'
import { ColorTable } from './ColorTable'

interface ResultsViewProps {
  result: AnalyzeResponse
}

export function ResultsView({ result }: ResultsViewProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-lg overflow-hidden border border-gray-200">
        <img
          src={`data:image/png;base64,${result.annotated_image}`}
          alt="Annotated wire image with bounding boxes"
          className="w-full h-auto"
        />
      </div>
      <ColorTable
        wireCounts={result.wire_counts}
        totalWires={result.total_wires}
      />
    </div>
  )
}
