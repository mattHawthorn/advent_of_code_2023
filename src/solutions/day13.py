from functools import partial
from itertools import chain, repeat
from operator import itemgetter, ne
from typing import IO, Iterable, Iterator, Optional, Sequence, Tuple

from util import Grid, parse_blocks

Reflection = Tuple[bool, int]


def mismatches(index: int, seq: Sequence) -> int:
    left, right = seq[index:], seq[index - 1 :: -1]  # noqa: E203
    return sum(map(ne, left, right))


def is_reflected(grid: Grid, tolerance: int, reflection: Reflection) -> bool:
    horizontal, index = reflection
    mismatches_ = partial(mismatches, index)
    seqs: Iterable[Sequence]
    if horizontal:
        width = len(grid[0])
        seqs = (list(map(itemgetter(i), grid)) for i in range(width))
    else:
        seqs = grid

    return sum(map(mismatches_, seqs)) == tolerance


def find_reflection(tolerance: int, grid: Grid) -> Tuple[bool, int]:
    height = len(grid)
    width = len(grid[0])
    is_reflected_ = partial(is_reflected, grid, tolerance)
    horizontal_reflections = zip(repeat(True), range(1, height))
    vertical_reflections = zip(repeat(False), range(1, width))
    return next(filter(is_reflected_, chain(horizontal_reflections, vertical_reflections)))


def score(reflection: Reflection) -> int:
    horizontal, index = reflection
    return index * 100 if horizontal else index


def parse(input: Iterable[str]) -> Iterator[Grid[str]]:
    return parse_blocks(input, str.splitlines)


def run(input: IO[str], part_2: bool = True, tolerance: Optional[int] = None) -> int:
    blocks = parse(input)
    tolerance_ = int(part_2) if tolerance is None else tolerance
    reflections = map(partial(find_reflection, tolerance_), blocks)
    return sum(map(score, reflections))


_TEST_INPUT = """
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 405
    assert run(f(_TEST_INPUT), part_2=True) == 400
