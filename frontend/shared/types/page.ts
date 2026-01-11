export type PageStatus = "draft" | "published"
import type { Block } from "./block"

export type PageSummary = {
  id: string
  title: string
  slug: string
  status: PageStatus
  updated_at: string // ISO string from backend
}

/**
 * Full page payload returned by:
 * GET /v1/pages/:id
 *
 * Mirrors backend normalizer output.
 */
export type PageDetail = {
  id: string
  title: string
  slug: string
  status: PageStatus
  version: number
  sections: PageSection[]
  updated_at: string
  published_at: string | null
}

export type PageSection = {
  id: string
  title: string
  order: number
  blocks: Block[]
}
