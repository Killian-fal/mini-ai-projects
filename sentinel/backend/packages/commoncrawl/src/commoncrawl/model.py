from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Page:
    headers: str
    html: str


@dataclass(frozen=True, slots=True)
class IndexRow:
    url: str
    site: str  # host (without www.)
    host: str
    domain: str
    tld: str
    path: str
    warc_file: str
    offset: int
    length: int
