import sys

if sys.version_info < (3, 9):
    from typing import Callable, Iterable
else:
    from collections.abc import Callable, Iterable

from enum import Enum
from typing import Any, Generic, Optional, Type, TypeVar

T = TypeVar("T")


class ArgumentType(str, Enum):
    AUTO = "AUTO"
    ONE_ARGUMENT = "ONE_ARGUMENT"
    VARIABLE_LENGTH_ARGUMENT = "VARIABLE_LENGTH_ARGUMENT"
    VARIABLE_LENGTH_KEYWORD_ARGUMENT = "VARIABLE_LENGTH_KEYWORD_ARGUMENT"


class GenericTypingIterable(Generic[T]):
    def __init__(self, t: Type[T]):
        self._t = t

    def _cast(self, d: Any) -> T:
        return self._t(d)  # type: ignore [call-arg]

    def __call__(
        self, iter: Iterable[Any], on_error: Optional[Callable[[Any, int, Exception], None]] = None
    ) -> Iterable[T]:
        if on_error is not None:
            for i, d in enumerate(iter):
                try:
                    yield self._cast(d)
                except Exception as e:
                    on_error(d, i, e)
        else:
            for d in iter:
                yield self._cast(d)


class GenericVariableLengthArgumentTypingIterable(Generic[T], GenericTypingIterable[T]):
    def _cast(self, d: Any) -> T:
        return self._t(*d)


class GenericVariableLengthArgumentKeywordTypingIterable(Generic[T], GenericTypingIterable[T]):
    def _cast(self, d: Any) -> T:
        return self._t(**d)


class GenericTypingIterableFactory:
    def __init__(self, argument_type: ArgumentType = ArgumentType.ONE_ARGUMENT):
        self._argument_type = argument_type

    def __getitem__(self, t: Type[T]) -> GenericTypingIterable[T]:
        if self._argument_type == ArgumentType.VARIABLE_LENGTH_ARGUMENT:
            return GenericVariableLengthArgumentTypingIterable[T](t)
        if self._argument_type == ArgumentType.VARIABLE_LENGTH_KEYWORD_ARGUMENT:
            return GenericVariableLengthArgumentKeywordTypingIterable[T](t)
        if self._argument_type == ArgumentType.ONE_ARGUMENT:
            return GenericTypingIterable[T](t)
        try:
            sig = signature(t)
        except ValueError:
            return GenericTypingIterable[T](t)
        return GenericTypingIterable[T](t)


TypingIterable = GenericTypingIterableFactory()
VariableLengthArgumentTypingIterable = GenericTypingIterableFactory(argument_type=ArgumentType.VARIABLE_LENGTH_ARGUMENT)
VariableLengthKeywordArgumentTypingIterable = GenericTypingIterableFactory(
    argument_type=ArgumentType.VARIABLE_LENGTH_KEYWORD_ARGUMENT
)
