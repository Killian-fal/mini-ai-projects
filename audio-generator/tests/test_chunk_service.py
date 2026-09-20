import pytest

from audio_api.audio.chunk_service import (
    MAX_CHUNK_CHARS,
    text_to_chunks,
    _get_byte_size,
)


def test_prompt_too_large_raises_error():
    prompt = "x" * MAX_CHUNK_CHARS
    with pytest.raises(ValueError):
        text_to_chunks("n'importe quel texte", prompt)


def test_paragraphs_kept_when_under_limit():
    prompt = "Intro"
    text = "Premier paragraphe.\n\nDeuxième paragraphe court."

    chunks = text_to_chunks(
        text, prompt, _get_byte_size("Deuxième paragraphe court.Intro")
    )

    assert chunks == [
        "Premier paragraphe.",
        "Deuxième paragraphe court.",
    ]


def test_long_paragraph_split_by_sentences():
    prompt = "Intro"
    sentence = "a" * 400 + "."
    text = f"{sentence} {sentence} {sentence}"

    chunks = text_to_chunks(
        text, prompt, _get_byte_size(sentence) + _get_byte_size("Intro") + 1
    )

    assert chunks == [sentence, sentence, sentence]

    available_chars = MAX_CHUNK_CHARS - len(prompt.encode("utf-8"))
    assert all(len(chunk.encode("utf-8")) <= available_chars for chunk in chunks)
