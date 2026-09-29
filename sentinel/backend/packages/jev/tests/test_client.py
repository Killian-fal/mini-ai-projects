import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from jev import JevError, Usage, ask, client

Q = {"injection": {"type": "noul", "instructions": "?"}}
TYPESAFE_REPLY = {"answers": {"injection": {"noul": 0.2}}, "usage": {"input_tokens": 12, "output_tokens": 1}}


class Provider(ThreadingHTTPServer):
    """Local model provider: records each request, answers with `reply` (None = cut connection)."""

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.reply: tuple[int, bytes] | None = (200, b"{}")
        self.received: list[tuple[dict[str, str], Any]] = []

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"

    def answer(self, body: object, status: int = 200) -> None:
        self.reply = (status, json.dumps(body).encode())


class _Handler(BaseHTTPRequestHandler):
    server: Provider

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.received.append(({k.lower(): v for k, v in self.headers.items()}, json.loads(body)))
        status, reply = self.server.reply or (200, b"")
        self.send_response(status)
        self.send_header("Content-Length", str(len(reply) + (0 if self.server.reply else 10)))
        self.end_headers()
        self.wfile.write(reply)

    def log_message(self, *_: object) -> None:
        pass


@pytest.fixture
def provider(monkeypatch: pytest.MonkeyPatch) -> Iterator[Provider]:
    server = Provider()
    threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True).start()
    monkeypatch.setattr(client, "URL", server.url)
    monkeypatch.setenv("TYPESAFE_API_KEY", "ts-key")
    yield server
    server.shutdown()
    server.server_close()


def test_the_reply_is_read_into_answers_and_usage(provider: Provider) -> None:
    provider.answer(TYPESAFE_REPLY)
    reply = ask("[hidden] rate me", Q)
    assert (reply.model, reply.answers, reply.usage) == (
        "jev-latest",
        {"injection": {"noul": 0.2}},
        Usage(12, 1),
    )
    assert provider.received[0][0]["authorization"] == "Bearer ts-key"


@pytest.mark.parametrize(("usage", "expected"), [({}, Usage(None, None)), (None, None)])
def test_a_missing_usage_is_read_as_unknown_counts(
    provider: Provider, usage: dict[str, int] | None, expected: Usage | None
) -> None:
    provider.answer({"answers": {"injection": {"noul": 0.2}}, "usage": usage})
    assert ask("[hidden] rate me", Q).usage == expected


def test_the_reply_carries_the_exact_body_sent(provider: Provider) -> None:
    provider.answer({"answers": {"injection": {"noul": 0.2}}})
    reply = ask("[hidden] rate me", Q)
    assert json.loads(reply.request) == provider.received[0][1]
    assert provider.received[0][1] == {"model": "jev-latest", "state": "[hidden] rate me", "questions": Q}


@pytest.mark.parametrize(
    "reply",
    [
        (429, b'{"error": "slow down"}'),
        (200, b"<html>not json</html>"),
        (200, b'{"error": "overloaded"}'),
        (200, b'{"answers": {"other": {"noul": 0.1}}}'),
        None,
    ],
    ids=str,
)
def test_a_failed_call_surfaces_as_a_jev_error(provider: Provider, reply: tuple[int, bytes] | None) -> None:
    provider.reply = reply
    with pytest.raises(JevError):
        ask("s", Q)


def test_a_missing_key_fails_before_calling_the_provider(
    provider: Provider, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TYPESAFE_API_KEY")
    with pytest.raises(JevError, match="TYPESAFE_API_KEY"):
        ask("s", Q)
    assert provider.received == []
