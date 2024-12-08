from functools import partial
from typing import IO, Iterable, Iterator

from util import LinkedList, assert_equal, sign


def parse_line(line: str) -> list[int]:
    return list(map(int, line.split()))


def parse(input: Iterable[str]) -> Iterator[list[int]]:
    return map(parse_line, map(str.strip, input))


def is_safe(
    levels: list[int], allow_removal: bool = False, min_diff: int = 1, max_diff: int = 3
) -> bool:
    def inner(
        levels: LinkedList[int] | None, allow_removal: bool, prev1: int | None, prev2: int | None
    ) -> bool:
        if levels is None:
            return True
        curr = levels.head
        if prev1 is None:
            compatible = True
        else:
            diff1 = curr - prev1
            compatible = min_diff <= abs(diff1) <= max_diff
            if prev2 is not None:
                diff2 = prev1 - prev2
                compatible = compatible and sign(diff1) == sign(diff2)  # same direction

        return (compatible and inner(levels.tail, allow_removal, curr, prev1)) or (
            allow_removal and inner(levels.tail, False, prev1, prev2)  # remove current
        )

    return inner(LinkedList.from_iterable(levels), allow_removal, None, None)


def run(input: IO[str], part_2: bool = True) -> int:
    levelss = parse(input)
    return sum(map(partial(is_safe, allow_removal=part_2), levelss))


_test_input = """
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9""".strip()


def test():
    import io

    assert is_safe([1, 2, 3, 4])
    assert is_safe([1, 3, 6, 7, 9])
    assert is_safe([10, 7, 4, 1])
    assert not is_safe([1, 5])
    assert not is_safe([1, 2, 3, 7, 8])
    assert not is_safe([8, 7, 6, 2, 1])
    assert not is_safe([1, 3, 5, 3, 1])
    assert is_safe([1, 5, 3, 4, 6], allow_removal=True)  # remove left
    assert is_safe([1, 3, 5, 6, 10], allow_removal=True)  # remove right
    assert is_safe([1, 3, 2, 4, 5], allow_removal=True)  # diffs correct size but sign change middle
    assert is_safe([8, 6, 4, 4, 1], allow_removal=True)  # zero diff middle
    assert is_safe([8, 6, 10, 4, 1], allow_removal=True)  # big diff with sign change middle
    assert not is_safe([1, 5, 3, 7, 4], allow_removal=True)
    assert not is_safe([1, 2, 7, 8, 9], allow_removal=True)
    assert not is_safe([9, 7, 6, 2, 1], allow_removal=True)

    f = io.StringIO
    assert_equal(run(f(_test_input), part_2=False), 2)
    assert_equal(run(f(_test_input), part_2=True), 4)
