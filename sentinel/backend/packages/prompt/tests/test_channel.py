from prompt import channels, line


def test_channels_are_listed_once_in_order_of_first_appearance() -> None:
    text = "\n".join([line("hidden", "a"), line("header", "X-AI: b"), line("hidden", "c")])
    assert channels(text) == ["hidden", "header"]
