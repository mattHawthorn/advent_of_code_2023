import operator
from collections import Counter
from typing import IO, Iterable


def parse(input: Iterable[str]) -> tuple[list[int], list[int]]:
    lines = list(map(str.split, map(str.strip, input)))
    if not lines:
        return [], []
    else:
        left, right = zip(*lines)
        return list(map(int, left)), list(map(int, right))


def _mul(a: int | None, b: int | None) -> int:
    return a * b if a and b else 0


def run(input: IO[str], part_2: bool = True) -> int:
    left, right = parse(input)
    if part_2:
        right_counts = Counter(right)
        return sum(map(_mul, left, map(right_counts.get, left)))
    else:
        return sum(map(abs, map(operator.sub, sorted(left), sorted(right))))


_test_input = """3   4
4   3
2   5
1   3
3   9
3   3"""


def test():
    import io

    f = io.StringIO
    assert run(f(_test_input), part_2=False) == 11
