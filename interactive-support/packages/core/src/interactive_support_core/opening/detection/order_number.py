import re

ORDER_NUMBER_PATTERN = re.compile(r"#?(CMA_[A-Z0-9]+)", re.IGNORECASE)


def extract_order_number(text: str) -> str | None:
    match = ORDER_NUMBER_PATTERN.search(text)
    return f"#{match.group(1).upper()}" if match else None
