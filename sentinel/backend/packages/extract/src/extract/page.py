import re

from extract.model import Chunk
from extract.parser import Parser, hides

STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
SIMPLE_SELECTOR = re.compile(r"[.#][\w-]+")


def extract(html: str, headers: str = "") -> list[Chunk]:
    parser = Parser(_hidden_selectors(html))
    parser.feed(html)
    parser.close()
    return [Chunk("header", h.strip()) for h in headers.splitlines() if ":" in h] + parser.chunks


def _hidden_selectors(html: str) -> set[str]:
    # ponytail: regex over the document's <style> blocks, simple selectors only; no external
    # stylesheets, no compound selectors, no cascade. Use a CSS parser when that falls short.
    found: set[str] = set()
    for sel, decl in RULE.findall("\n".join(STYLE_BLOCK.findall(html))):
        if hides(decl):
            found |= {s for part in sel.split(",") if SIMPLE_SELECTOR.fullmatch(s := part.strip())}
    return found
