export type BlockType =
  | "text"
  | "image"
  | "gallery"
  | "cta"
  | "custom"

export type BaseBlock = {
  id: string
  type: BlockType
  order: number
}

/**
 * Individual block variants.
 * Keep payloads backend-shaped.
 */
export type TextBlock = BaseBlock & {
  type: "text"
  data: {
    html: string
  }
}

export type ImageBlock = BaseBlock & {
  type: "image"
  data: {
    media_id: string
    alt: string | null
  }
}

export type Block =
  | TextBlock
  | ImageBlock
