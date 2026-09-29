# most to least suspect: a line is never dropped in favour of a more benign channel.
CHANNELS = ("[header]", "[comment]", "[hidden]", "[attr]", "[script]", "[meta]", "[visible]")
VISIBLE = "[visible]"


def line(channel: str, text: str) -> str:
    return f"[{channel}] {text}"


def channels(text: str) -> list[str]:
    """Channel names in `text`, once each, in order of first appearance."""
    return list(dict.fromkeys(split(row)[0][1:-1] for row in text.splitlines()))


def split(row: str) -> tuple[str, str]:
    """`[channel] body` as (channel, body); a line without prefix is visible."""
    head, sep, body = row.partition("] ")
    return (f"{head}]", body) if sep else (VISIBLE, row)
