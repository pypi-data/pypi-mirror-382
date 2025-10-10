import pytest

from yaml_lex.format import contains_markdown_table, wrap_block, wrap_value


@pytest.mark.parametrize(
    "text,char_limit,expected_in",
    [
        ("This is a long line that should be wrapped.", 10, "This is a"),
        ("Another example string to test wrapping.", 15, "Another example"),
    ],
)
def test_wrap_block_wraps(text, char_limit, expected_in):
    wrapped = wrap_block(text, char_limit)
    assert "\n" in wrapped
    assert expected_in in wrapped


def test_wrap_block_preserves_paragraphs():
    text = "Paragraph one.\n\nParagraph two."
    wrapped = wrap_block(text, 10)

    # Paragraph break preserved
    assert "\n\n" in wrapped

    # Both pieces exist, even if wrapped
    assert "Paragraph" in wrapped
    assert "one." in wrapped
    assert "two." in wrapped


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("| Col1 | Col2 |\n| --- | --- |\n| A | B |", True),
        ("normal text", False),
        ("| just one row | no header |", False),
    ],
)
def test_contains_markdown_table(input_text, expected):
    assert contains_markdown_table(input_text) is expected


@pytest.mark.parametrize(
    "key,value,char_limit,expected_substr",
    [
        (
            "caption",
            "This is a very long caption that should be wrapped",
            20,
            "wrapped",
        ),
        ("content", "This content is quite lengthy and will wrap", 15, "content"),
    ],
)
def test_wrap_value(key, value, char_limit, expected_substr):
    result = wrap_value(key, value, char_limit)
    assert expected_substr in str(result)
    assert "\n" in str(result)
