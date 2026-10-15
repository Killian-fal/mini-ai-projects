import math


def wilson(passed: int, total: int) -> tuple[float, float]:
    z = 1.96
    rate = passed / total
    center = (rate + z * z / (2 * total)) / (1 + z * z / total)
    margin = (
        z
        * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total))
        / (1 + z * z / total)
    )
    return max(0.0, center - margin), min(1.0, center + margin)
