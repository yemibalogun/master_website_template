import { http } from "./http"
import type {
    PageSummary,
    PageDetail,
    CursorPage,
} from "@shared/types"

/**
 * GET /v1/pages?cursor=...
 */
export async function listPages(
    params: {
        cursor?: string
        token: string
        tenantId: string
    }
): Promise<CursorPage<PageSummary>> {
    const query = params.cursor
        ? `?cursor=${encodeURIComponent(params.cursor)}`
        : ""

    return http<CursorPage<PageSummary>>(`/v1/pages${query}`, {
        token: params.token,
        tenantId: params.tenantId,
    })
}

/**
 * GET /v1/pages/:id
 */
export async function getPage(
    params: {
        pageId: string
        token: string
        tenantId: string
    }
): Promise<PageDetail> {
    return http<PageDetail>(`/v1/pages/${params.pageId}`, {
        token: params.token,
        tenantId: params.tenantId,
    })
}

/**
 * POST /v1/pages
 */
export async function createPage(
    params: {
        title: string
        slug: string
        token: string
        tenantId: string
    }
): Promise<PageDetail> {
    return http<PageDetail>("/v1/pages", {
        method: "POST",
        body: {
            title: params.title,
            slug: params.slug,
        },
        token: params.token,
        tenantId: params.tenantId,
    })
}

/**
 * POST /v1/pages/:id/publish
 */
export async function publishPage(
    params: {
        pageId: string
        token: string
        tenantId: string
    }
): Promise<void> {
    await http<void>(`/v1/pages/${params.pageId}/publish`, {
        method: "POST",
        token: params.token,
        tenantId: params.tenantId,
    })
}
