import re
from html.parser import HTMLParser

from extract.model import Chunk

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
DROP = {"script", "style"}
HIDDEN_TAGS = {"noscript", "template"}
TEXT_ATTRS = ("alt", "title", "aria-label", "placeholder", "value")
META_NAMES = ("name", "property", "http-equiv", "itemprop")
HIDDEN_STYLE = re.compile(
    r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?![.\d])"
    r"|font-size\s*:\s*(?:0|1|0?\.\d+)(?:px|pt|em|%)?\b"
    r"|text-indent\s*:\s*-\d{4,}"
    r"|clip\s*:\s*rect\(\s*0[\s,]+0[\s,]+0[\s,]+0"
    r"|clip-path\s*:\s*inset\(\s*100%"
)
OFFSCREEN = re.compile(r"position\s*:\s*(?:absolute|fixed)"), re.compile(r"(?:left|top)\s*:\s*-\d{4,}")
ZERO_BOX = re.compile(r"(?:height|width)\s*:\s*0(?![.\d])"), re.compile(r"overflow\s*:\s*hidden")


class Parser(HTMLParser):
    def __init__(self, css: set[str]) -> None:
        super().__init__()
        self.css = css
        self.chunks: list[Chunk] = []
        self.stack: list[tuple[str, str | None]] = []

    def _current(self) -> str | None:
        return self.stack[-1][1] if self.stack else "visible"

    def _add(self, channel: str | None, text: str) -> None:
        clean = " ".join(text.split())
        if channel and clean:
            self.chunks.append(Chunk(channel, clean))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "meta":
            name = next((a[k] for k in META_NAMES if a.get(k)), "")
            content = a.get("content", "")
            self._add("meta", f"{name}: {content}" if name and content else content)
        for key in TEXT_ATTRS:
            self._add("attr", a.get(key, ""))
        if tag not in VOID:
            self.stack.append((tag, _channel(tag, a, self._current(), self.css)))

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data: str) -> None:
        self._add(self._current(), data)

    def handle_comment(self, data: str) -> None:
        self._add("comment", data)


def hides(decl: str) -> bool:
    return bool(
        HIDDEN_STYLE.search(decl)
        or all(r.search(decl) for r in OFFSCREEN)
        or all(r.search(decl) for r in ZERO_BOX)
    )


def _names(attrs: dict[str, str]) -> set[str]:
    return {f".{c}" for c in attrs.get("class", "").split()} | {f"#{i}" for i in attrs.get("id", "").split()}


def _channel(tag: str, attrs: dict[str, str], parent: str | None, css: set[str]) -> str | None:
    if tag in DROP:
        return "script" if tag == "script" and "ld+json" in attrs.get("type", "") else None
    if parent is None or parent == "hidden":
        return parent
    hidden = (
        tag in HIDDEN_TAGS
        or "hidden" in attrs
        or attrs.get("aria-hidden") == "true"
        or bool(_names(attrs) & css)
        or hides(attrs.get("style", ""))
    )
    return "hidden" if hidden else parent
