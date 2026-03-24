export interface BoundingBox {
  color: string
  x: number
  y: number
  w: number
  h: number
}

export interface AnalyzeResponse {
  colors_found: string[]
  wire_counts: Record<string, number>
  total_wires: number
  bounding_boxes: BoundingBox[]
  annotated_image: string
}

export interface ColorRange {
  name: string
  lower: [number, number, number]
  upper: [number, number, number]
}

export interface ColorsResponse {
  colors: ColorRange[]
}
