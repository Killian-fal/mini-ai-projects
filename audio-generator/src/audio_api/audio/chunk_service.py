from langchain_text_splitters import RecursiveCharacterTextSplitter

from audio_api.environment import MAX_CHUNK_CHARS


def text_to_chunks(
    text: str, prompt: str, max_chunk_chars: int = MAX_CHUNK_CHARS
) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_chars - _get_byte_size(prompt),
        chunk_overlap=0,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = splitter.create_documents([text])
    return [chunk.page_content for chunk in chunks]


def _get_byte_size(text: str) -> int:
    return len(text.encode("utf-8"))
