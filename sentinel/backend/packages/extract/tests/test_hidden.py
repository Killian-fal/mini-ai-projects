from extract import extract


def channel_of(html: str, needle: str) -> str | None:
    return next((c.channel for c in extract(html) if needle in c.text), None)


def test_class_hidden_by_style_block() -> None:
    html = "<style>.x{display:none}</style><div class='a x'>secret</div>"
    assert channel_of(html, "secret") == "hidden"


def test_id_hidden_by_style_block() -> None:
    html = "<style>h1, #box { visibility: hidden; }</style><div id='box'>secret</div>"
    assert channel_of(html, "secret") == "hidden"


def test_hidden_attribute() -> None:
    assert channel_of("<div hidden>secret</div>", "secret") == "hidden"


def test_offscreen_class() -> None:
    html = "<style>.off{position:absolute;left:-9999px}</style><div class='off'>secret</div>"
    assert channel_of(html, "secret") == "hidden"


def test_visible_class_stays_visible() -> None:
    html = "<style>.off{position:absolute;left:12px}</style><div class='off'>secret</div>"
    assert channel_of(html, "secret") == "visible"


def test_meta_carries_its_name_before_its_content() -> None:
    html = (
        "<meta name='description' content='hello'>"
        "<meta property='og:title' content='hi'><meta content='bare'>"
    )
    assert [c.text for c in extract(html)] == ["description: hello", "og:title: hi", "bare"]
