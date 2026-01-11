// frontend/admin/lib/mocks/pages.ts

export type PageStatus = "draft" | "published"

export interface PageItem {
  id: string
  title: string
  slug: string               // required and intentional
  status: PageStatus
  updated_at: string
}

export interface PagesResponse {
  items: PageItem[]
  has_more: boolean
}

export const mockPagesResponse: PagesResponse = {
  items: [
    {
      id: "page_1",
      title: "Home",
      slug: "home",
      status: "published",
      updated_at: new Date().toISOString(),
    },
    {
      id: "page_2",
      title: "About",
      slug: "about",
      status: "draft",
      updated_at: new Date().toISOString(),
    },
  ],
  has_more: true,
}
