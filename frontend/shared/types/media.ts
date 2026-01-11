export type MediaType = "image" | "video" | "file"

export type MediaItem = {
  id: string
  type: MediaType
  url: string
  filename: string
  mime_type: string
  size: number          // bytes
  created_at: string    // ISO string
}
