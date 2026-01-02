from .block import normalize_block

def normalize_section(section, admin=False, include_blocks=False):
    data = {
        "id": section.id,
        "type": section.type,
        "order": section.order,
        "settings": section.settings or {}
    }

    if include_blocks:
        blocks = sorted(section.blocks, key=lambda b: b.order)
        data["blocks"] = [
            normalize_block(b, admin=admin) for b in blocks
        ]

    return data
