/** @package */
export type Part = { text: string; hit: boolean };

/** Splits a text into highlighted / non-highlighted fragments. */
/** @package */
export function split(text: string, needle: string): Part[] {
  if (needle === "") {
    return [{ text, hit: false }];
  }
  const parts: Part[] = [];
  const haystack = text.toLowerCase();
  const lower = needle.toLowerCase();
  let from = 0;
  let at = haystack.indexOf(lower);
  while (at >= 0) {
    if (at > from) {
      parts.push({ text: text.slice(from, at), hit: false });
    }
    parts.push({ text: text.slice(at, at + needle.length), hit: true });
    from = at + needle.length;
    at = haystack.indexOf(lower, from);
  }
  if (from < text.length) {
    parts.push({ text: text.slice(from), hit: false });
  }
  return parts;
}

/** @package */
export type TokenKind = "key" | "string" | "number" | "literal" | "punctuation";

/** @package */
export type Token = { text: string; kind: TokenKind };

const JSON_TOKEN =
  /("(?:[^"\\]|\\.)*"\s*:)|("(?:[^"\\]|\\.)*")|(-?\d+(?:\.\d+)?)|(true|false|null)/gu;

/** @package */
export function jsonTokens(value: unknown): Token[] {
  const source = JSON.stringify(value ?? null, null, 2) ?? "null";
  const tokens: Token[] = [];
  let last = 0;
  JSON_TOKEN.lastIndex = 0;
  let match = JSON_TOKEN.exec(source);
  while (match !== null) {
    if (match.index > last) {
      tokens.push({ text: source.slice(last, match.index), kind: "punctuation" });
    }
    tokens.push({ text: match[0], kind: kindOf(match) });
    last = match.index + match[0].length;
    match = JSON_TOKEN.exec(source);
  }
  if (last < source.length) {
    tokens.push({ text: source.slice(last), kind: "punctuation" });
  }
  return tokens;
}

function kindOf(match: RegExpExecArray): TokenKind {
  if (match[1] !== undefined) {
    return "key";
  }
  if (match[2] !== undefined) {
    return "string";
  }
  return match[3] === undefined ? "literal" : "number";
}
