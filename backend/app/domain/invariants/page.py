from .section import assert_section
from .exceptions import InvariantViolation

def assert_page(page, publish=False):
    sections = page.sections

    if publish and not sections:
        raise InvariantViolation("Cannot publish page without sections.")
    
    orders = [section.order for section in sections]
    expected = list(range(1, len(orders) + 1))

    if sorted(orders) != expected:
        raise InvariantViolation(
            f"Section orders are not consecutive starting from 1: {orders}"
        )
    
    for section in sections:
        assert_section(section)