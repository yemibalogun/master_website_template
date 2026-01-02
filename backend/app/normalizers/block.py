def normalize_block(block, admin=False):
    base = {
        "id": block.id,
        "type": block.type,
        "order": block.order,
        "content": block.content,
        "media_url": block.media_url
    }

    if admin:
        base["created_at"] = block.created_at
        base["updated_at"] = block.updated_at

    return base
