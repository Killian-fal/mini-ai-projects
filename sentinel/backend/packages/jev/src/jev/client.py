import json
import os
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from jev.error import JevError
from jev.model import Reply, Usage

URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
MAX_CHARS = 30_000  # ponytail: context size is undocumented, callers truncate to this


def ask(state: str, questions: dict[str, dict[str, Any]]) -> Reply:
    body = json.dumps({"model": MODEL, "state": state, "questions": questions})
    req = Request(
        URL,
        data=body.encode(),
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
    )
    try:
        # ponytail: no retry on 429/529, add a backoff if it happens
        with urlopen(req, timeout=30) as r:
            reply: dict[str, Any] = json.load(r)
    except HTTPError as e:
        with e:
            raise JevError(f"{e.code} {e.read()[:200]!r}") from e
    except (OSError, HTTPException, ValueError) as e:  # ValueError: unreadable JSON
        raise JevError(str(e)) from e
    if not _answered(reply, questions):
        raise JevError(f"réponse incomplète: {json.dumps(reply)[:200]}")
    usage = reply.get("usage")
    return Reply(
        model=reply.get("model", MODEL),
        answers=reply["answers"],
        usage=None if usage is None else Usage(usage.get("input_tokens"), usage.get("output_tokens")),
        request=body,
    )


def _key() -> str:
    if key := os.environ.get("TYPESAFE_API_KEY"):
        return key
    raise JevError("TYPESAFE_API_KEY manquante")


def _answered(reply: dict[str, Any], questions: dict[str, dict[str, Any]]) -> bool:
    """Each question has its answer under its type, e.g. answers.injection.noul."""
    try:
        return all(spec["type"] in reply["answers"][name] for name, spec in questions.items())
    except (KeyError, TypeError):
        return False
