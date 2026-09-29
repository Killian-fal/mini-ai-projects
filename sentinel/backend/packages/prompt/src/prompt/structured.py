# ponytail: standard headers with structured values; any other name (x-ai, x-llm…) goes to Jev.
STRUCTURED_HEADERS = frozenset(
    {
        "date",
        "expires",
        "last-modified",
        "age",
        "etag",
        "content-type",
        "content-length",
        "content-encoding",
        "content-language",
        "transfer-encoding",
        "connection",
        "keep-alive",
        "vary",
        "cache-control",
        "pragma",
        "set-cookie",
        "accept-ranges",
        "alt-svc",
        "strict-transport-security",
        "x-frame-options",
        "x-content-type-options",
        "x-xss-protection",
        "referrer-policy",
        "content-security-policy",
        "content-security-policy-report-only",
        "permissions-policy",
        "x-cache",
        "x-cache-hits",
        "x-served-by",
        "x-request-id",
        "x-timer",
        "cf-ray",
        "cf-cache-status",
        "via",
        "x-varnish",
        "x-powered-by",
        "x-turbo-charged-by",
        "link",
        "p3p",
        "upgrade",
        "x-ua-compatible",
        "server-timing",
        "x-gateway-cache-key",
        "nel",
        "report-to",
        "x-cdn",
        "x-runtime",
        "x-download-options",
        "x-permitted-cross-domain-policies",
    }
)
# ponytail: metas with constrained values; description, titles, author, generator and robots stay.
STRUCTURED_META = frozenset(
    {
        "viewport",
        "charset",
        "theme-color",
        "color-scheme",
        "format-detection",
        "referrer",
        "csrf-token",
        "csrf-param",
        "og:url",
        "og:type",
        "og:locale",
        "twitter:card",
        "twitter:image",
        "twitter:site",
        "mobile-web-app-capable",
        "google-site-verification",
        "facebook-domain-verification",
        "fb:app_id",
        "article:published_time",
        "article:modified_time",
    }
)
RULES = {
    "[header]": (
        STRUCTURED_HEADERS,
        ("cross-origin-", "access-control-", "x-crawler-", "x-litespeed-", "x-amz-", "x-edge-"),
    ),
    "[meta]": (STRUCTURED_META, ("msapplication-", "apple-mobile-web-app-", "og:image")),
}


def structured(channel: str, body: str) -> bool:
    """A header or meta whose name says its value is constrained."""
    rule = RULES.get(channel)
    if rule is None:
        return False
    names, prefixes = rule
    name = body.partition(": ")[0].strip().lower()
    return name in names or name.startswith(prefixes)
