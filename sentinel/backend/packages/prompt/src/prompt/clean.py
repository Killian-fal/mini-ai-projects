import re
from urllib.parse import unquote

from prompt.channel import split
from prompt.reduce import reduced
from prompt.structured import structured

URL = re.compile(r"(?:https?:)?//[^\s\"'<>()\[\]]{6,}")
SEGMENT = re.compile(r"[/?&=#]")
WORD = re.compile(r"[^\W\d_]{2,}")
LETTER = re.compile(r"[^\W\d_]")
BLOB = re.compile(r"[^\s<>]{100,}")
BLANKS = re.compile(r"(?:[ \t]|\\[ntr]){3,}")
SEPARATORS = str.maketrans("+-_", "   ")
SENTENCE_WORDS = 3


def clean(text: str) -> list[str]:
    """Lines minus silent ones, sentence-less URLs, blobs, duplicates and echoes; channel prefix kept."""
    seen: set[str] = set()
    kept: list[str] = []
    for line in text.split("\n"):
        if _dropped(line):
            continue
        short = BLANKS.sub(" ", BLOB.sub(_blob, URL.sub(_shrink, line)))
        if (key := short.strip()) and key not in seen:
            seen.add(key)
            kept.append(short)
    return reduced(kept)


def _dropped(line: str) -> bool:
    """A line without letters, or a header or meta whose value is constrained."""
    channel, body = split(line)
    return not LETTER.search(body) or structured(channel, body)


def _shrink(m: re.Match[str]) -> str:
    """The URL itself if one of its segments reads as a sentence, `<url>` otherwise."""
    tail = unquote(m[0]).partition("//")[2].partition("/")[2]
    phrase = any(
        len(WORD.findall(seg.translate(SEPARATORS))) >= SENTENCE_WORDS for seg in SEGMENT.split(tail)
    )
    return m[0] if phrase else "<url>"


def _blob(m: re.Match[str]) -> str:
    """The run itself if at least three whole words cover half its characters, `<blob>` otherwise."""
    # ponytail: a sentence URL followed by a long tracking parameter falls under half and becomes
    # <blob>; test segment by segment if that case shows up.
    run = unquote(m[0])
    words = [w for w in SEGMENT.sub(" ", run).translate(SEPARATORS).split() if WORD.fullmatch(w)]
    sentence = len(words) >= SENTENCE_WORDS and 2 * sum(map(len, words)) >= len(run)
    return m[0] if sentence else "<blob>"
