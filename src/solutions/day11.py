from collections import Counter, defaultdict
from itertools import chain, islice
from typing import IO, Iterable, Iterator, Literal, Mapping

import util

NumType = Literal["zero", "even_digits", "positive_odd_digits"]


def step(num: int) -> tuple[int, ...]:
    if num == 0:
        return (1,)
    s = str(num)
    len_ = len(s)
    if len_ % 2 == 0:
        half = len_ // 2
        return int(s[:half]), int(s[half:])
    return (2024 * num,)


def evolve(stones: Iterable[int]) -> Iterator[Mapping[int, int]]:
    counts = Counter(stones)

    def inner(counts):
        new = defaultdict(int)
        for num, count in counts.items():
            for n in step(num):
                new[n] += count
        return new

    yield from util.iterate(inner, counts)


def parse(input: Iterable[str]) -> list[int]:
    return list(map(int, chain.from_iterable(map(str.split, map(str.strip, input)))))


def run(input: IO[str], part_2: bool = True) -> int:
    stones = parse(input)
    steps = 75 if part_2 else 25
    states = islice(evolve(stones), steps + 1)
    counts = util.last(states)
    return sum(counts.values())


_test_input = "125 17"


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False), 55312)
