from .block import assert_block_order, assert_block_media
from .exceptions import InvariantViolation

def assert_section(section):
    blocks = section.blocks

    if not blocks:
        raise InvariantViolation("Section must contain at least one block.")
    
    assert_block_order(blocks)

    for block in blocks:
        assert_block_media(block)