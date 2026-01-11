/**
 * Generic cursor-based pagination response
 * used across admin list screens.
 */
export type CursorPage<T> = {
  items: T[]
  next_cursor: string | null
}
