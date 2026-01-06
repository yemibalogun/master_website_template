from .exceptions import InvariantViolation

def assert_block_order(blocks):
    orders = [block.order for block in blocks]
    if not orders:
        return
    
    expected = list(range(1, len(orders) + 1))
    if sorted(orders) != expected:
        raise InvariantViolation(
            f"Block orders are not consecutive starting from 1: {orders}"
        )
    
def assert_block_media(block):
    if block.type in ("image", "video"):
        if not block.media_url:
            raise InvariantViolation(
                f"{block.type} block must have media_url set."
            )
    else:
        if block.media_url:
            raise InvariantViolation(
                f"{block.type} block should not have media_url set."
            )