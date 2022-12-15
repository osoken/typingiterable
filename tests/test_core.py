from typing import Any

import pytest

import typingiterable


class TwoArgumentDataType:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TwoArgumentDataType):
            return False
        return self.x == other.x and self.y == other.y


class KeywordOnlyArgumentDataType(TwoArgumentDataType):
    def __init__(self, *, x: int, y: int, text: str):
        super(KeywordOnlyArgumentDataType, self).__init__(x, y)
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    def __eq__(self, other: Any) -> bool:
        if not super(KeywordOnlyArgumentDataType, self).__eq__(other):
            return False
        if not isinstance(other, KeywordOnlyArgumentDataType):
            return False
        return self.text == other.text


def test_iterate() -> None:
    actual = list(typingiterable.TypingIterable[int](["122", "231", "0", "2", 2.3]))
    assert actual == [122, 231, 0, 2, 2]


def test_default_error_handling() -> None:
    actual = []
    with pytest.raises(Exception):
        for d in typingiterable.TypingIterable[int](["123", "321", "1.23", "432"]):
            actual.append(d)
    assert actual == [123, 321]


def test_pass_error_handler() -> None:
    actual = []
    errors = []

    def handler(d: str, idx: int, err: Exception) -> None:
        errors.append((d, idx))

    for d in typingiterable.TypingIterable[int](["123", "321", "1.23", "432"], on_error=handler):
        actual.append(d)
    assert actual == [123, 321, 432]
    assert errors == [("1.23", 2)]


def test_variable_length_arguments() -> None:
    actual = []
    for d in typingiterable.VariableLengthArgumentTypingIterable[TwoArgumentDataType]([(10, 12), (-1, 3), (-3, -3)]):
        actual.append(d)

    assert actual == [TwoArgumentDataType(10, 12), TwoArgumentDataType(-1, 3), TwoArgumentDataType(-3, -3)]


def test_variable_length_keyword_arguments() -> None:
    actual = []
    for d in typingiterable.VariableLengthKeywordArgumentTypingIterable[TwoArgumentDataType](
        [{"x": 10, "y": 12}, {"x": -1, "y": 3}, {"x": -3, "y": -3}, {"y": 0, "x": 0}]
    ):
        actual.append(d)

    assert actual == [
        TwoArgumentDataType(10, 12),
        TwoArgumentDataType(-1, 3),
        TwoArgumentDataType(-3, -3),
        TwoArgumentDataType(0, 0),
    ]


def test_keyword_only_arguments() -> None:
    actual = []
    for d in typingiterable.VariableLengthKeywordArgumentTypingIterable[KeywordOnlyArgumentDataType](
        [
            {"x": 10, "y": 12, "text": "one"},
            {"x": -1, "y": 3, "text": "two"},
            {"x": -3, "y": -3, "text": "three"},
            {"y": 0, "x": 0, "text": "four"},
        ]
    ):
        actual.append(d)

    assert actual == [
        KeywordOnlyArgumentDataType(x=10, y=12, text="one"),
        KeywordOnlyArgumentDataType(x=-1, y=3, text="two"),
        KeywordOnlyArgumentDataType(x=-3, y=-3, text="three"),
        KeywordOnlyArgumentDataType(x=0, y=0, text="four"),
    ]
