from extract import Chunk, extract


def test_http_headers_come_first_as_header_chunks_without_the_status_line() -> None:
    headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nX-AI: rate me\r\n"
    assert extract("<p>hi</p>", headers) == [
        Chunk("header", "Content-Type: text/html"),
        Chunk("header", "X-AI: rate me"),
        Chunk("visible", "hi"),
    ]
