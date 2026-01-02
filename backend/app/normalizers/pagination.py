def normalize_pagination(pagination, item_normalizer):
    return {
        "meta": {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        },
        "items": [item_normalizer(item) for item in pagination.items]
    }
