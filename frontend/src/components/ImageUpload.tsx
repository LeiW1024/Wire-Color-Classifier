'use client'

import { useCallback, useRef } from 'react'

interface ImageUploadProps {
  onFileSelected: (file: File) => void
  isLoading?: boolean
}

export function ImageUpload({ onFileSelected, isLoading = false }: ImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        onFileSelected(file)
      }
    },
    [onFileSelected]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      const file = e.dataTransfer.files?.[0]
      if (file) {
        onFileSelected(file)
      }
    },
    [onFileSelected]
  )

  return (
    <div
      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      <input
        ref={inputRef}
        data-testid="file-input"
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={handleChange}
        className="hidden"
      />
      {isLoading ? (
        <p className="text-gray-500">Processing image...</p>
      ) : (
        <div>
          <p className="text-lg font-medium">Upload wire image</p>
          <p className="text-sm text-gray-500 mt-1">
            Drag and drop or click to select (PNG, JPEG, WebP)
          </p>
        </div>
      )}
    </div>
  )
}
