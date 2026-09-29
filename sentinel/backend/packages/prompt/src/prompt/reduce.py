from collections.abc import Callable

from prompt.channel import CHANNELS, split

SUSPECT = {c: i for i, c in enumerate(CHANNELS)}
# headers are only reduced by _shadowed: never in favour of a less suspect channel.
VALUED = ("[meta]",)
MIN_ECHO = 20


def reduced(lines: list[str]) -> list[str]:
    """Drops lines whose text is still literally present in another sent line."""
    return _shadowed(_echoed(lines))


def _echoed(lines: list[str]) -> list[str]:
    """Drops metas whose value is already written verbatim in another sent line."""
    echoes = [body.partition(": ")[2].strip() if ch in VALUED else "" for ch, body in map(split, lines)]
    return _drop(lines, echoes, lambda i, j: j != i and echoes[i] in lines[j])


def _shadowed(lines: list[str]) -> list[str]:
    """Drops bodies strictly contained in a line of a channel at least as suspect."""
    parts = [split(line) for line in lines]
    bodies = [body.strip() for _, body in parts]
    ranks = [SUSPECT.get(channel, len(CHANNELS)) for channel, _ in parts]
    return _drop(
        lines,
        bodies,
        lambda i, j: bodies[i] != bodies[j] and bodies[i] in bodies[j] and ranks[j] <= ranks[i],
    )


def _drop(lines: list[str], needles: list[str], carried: Callable[[int, int], bool]) -> list[str]:
    """Drops line i when its needle is long enough and a surviving line j carries it."""
    alive = [True] * len(lines)
    # ponytail: O(n²) per page (a few thousand lines at most); inverted index if it gets hot.
    for i, needle in enumerate(needles):
        if len(needle) >= MIN_ECHO and any(alive[j] and carried(i, j) for j in range(len(lines))):
            alive[i] = False
    return [line for line, keep in zip(lines, alive, strict=True) if keep]
