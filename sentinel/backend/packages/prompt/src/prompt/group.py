from prompt.channel import split


def group(lines: list[str], max_chars: int) -> tuple[str, list[str]]:
    """One header per channel then its lines, cut at max_chars on a line end.

    Returns the text to send and the prefixed lines it carries.
    """
    groups: dict[str, list[str]] = {}
    used: list[str] = []
    total = 0
    for line in lines:
        channel, body = split(line)
        cost = len(body) + 1 + (0 if channel in groups else len(channel) + 1)
        if total + cost > max_chars:
            break
        groups.setdefault(channel, []).append(body)
        used.append(line)
        total += cost
    return "\n".join(x for channel, bodies in groups.items() for x in (channel, *bodies)), used
