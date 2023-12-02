from functools import partial, reduce
from itertools import chain
from typing import IO, DefaultDict, Iterable, Iterator, Mapping

DIGITS = dict(zip(map(str, range(0, 10)), range(0, 10)))
READABLE_DIGITS = {
    **DIGITS,
    **dict(
        zip(
            ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
            range(0, 10),
        ),
    ),
}


class Trie(DefaultDict[str, "Trie"]):
    def __init__(self):
        self.default_factory = Trie


def to_trie(strings: Iterable[str]):
    def update(trie: Trie, chars: Iterable[str]):
        chars = iter(chars)
        c = next(chars, None)
        if c is not None:
            subtrie = trie[c]
            update(subtrie, chars)
        return trie

    return reduce(update, strings, Trie())


def find_prefixes_in(strings: Trie, in_: str, offset: int = 0, prefix: str = "") -> Iterator[str]:
    if prefix and not strings:
        yield prefix
    elif offset < len(in_):
        next_ = in_[offset]
        if next_ in strings:
            yield from find_prefixes_in(strings[next_], in_, offset + 1, f"{prefix}{next_}")


def find_strings(strings: Trie, in_: str) -> Iterator[str]:
    return chain.from_iterable(find_prefixes_in(strings, in_, i) for i in range(len(in_)))


def parse_line(strings: Trie, digits: Mapping[str, int], line: str) -> int:
    digits_ = list(find_strings(strings, line))
    return int(f"{digits[digits_[0]]}{digits[digits_[-1]]}")


def parse(input: Iterable[str], digits: Mapping[str, int]) -> Iterator[int]:
    return map(partial(parse_line, to_trie(digits), digits), map(str.strip, input))


def run(input: IO[str], part_2: bool = True) -> int:
    digits = READABLE_DIGITS if part_2 else DIGITS
    ints = parse(input, digits)
    return sum(ints)


def test():
    import io

    trie = to_trie(["foo", "for", "fort"])
    assert list(find_prefixes_in(trie, "forty")) == ["fort"]

    input_ = "foo0bar1\nthreeightsevenine10"
    f = io.StringIO
    assert run(f(input_), part_2=False) == 1 + 10
    assert run(f(input_), part_2=True) == 1 + 30
