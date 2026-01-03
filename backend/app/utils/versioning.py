def snapshot_page(page):
    return {
        "page": {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "seo": page.seo,
            "status": page.status,
        },
        "sections": [
            {
                "id": s.id,
                "type": s.type,
                "order": s.order,
                "settings": s.settings,
                "blocks": [
                    {
                        "id": b.id,
                        "type": b.type,
                        "order": b.order,
                        "content": b.content,
                        "media_url": b.media_url,
                    }
                    for b in s.blocks
                ],
            }
            for s in page.sections
        ],
    }

def next_version(page_id, tenant_id):
    from app.models.page_version import PageVersion

    last = (
        PageVersion.query
        .filter_by(page_id=page_id, tenant_id=tenant_id)
        .order_by(PageVersion.version.desc())
        .first()
    )
    return (last.version + 1) if last else 1