from .section import normalize_section

def normalize_page(page, admin=False, preview=False):
    sections = sorted(page.sections, key=lambda s: s.order)

    return {
        "id": page.id,
        "title": page.title,
        "slug": page.slug,
        "status": page.status if admin else None,
        "seo": page.seo or {},
        "sections": [
            normalize_section(
                s,
                admin=admin,
                include_blocks=True
            )
            for s in sections
        ]
    }
