from functools import partial
from itertools import chain, islice, product, starmap
from operator import eq
from typing import IO, Iterator

from util import Grid, GridCoordinates, T, Vector, in_bounds, index, iterate, translate

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
DIAGONALS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def parse(input: IO[str]) -> Grid[str]:
    return list(map(str.strip, input))


def path(
    grid: Grid[T], height: int, width: int, length: int, coords: GridCoordinates, vec: Vector
) -> Iterator[T] | None:
    steps = length - 1
    if not in_bounds(width, height, translate((vec[0] * steps, vec[1] * steps), coords)):
        return None
    get = partial(index, grid)
    coordss = iterate(partial(translate, vec), coords)
    return map(get, islice(coordss, length))


def find(
    string: str, grid: Grid[str], directions=DIRECTIONS
) -> Iterator[tuple[GridCoordinates, Vector]]:
    height, width, length = len(grid), len(grid[0]), len(string)
    for x, y, direction in product(range(height), range(width), directions):
        p = path(grid, height, width, length, (x, y), direction)
        if p is not None and all(map(eq, string, p)):
            yield (x, y), direction


def x_complements(
    length: int, coords: GridCoordinates, direction: Vector
) -> Iterator[tuple[GridCoordinates, Vector]]:
    steps = length - 1
    yield translate((0, direction[1] * steps), coords), (direction[0], -direction[1])
    yield translate((direction[0] * steps, 0), coords), (-direction[0], direction[1])


def run(input: IO[str], part_2: bool = True) -> int:
    grid = parse(input)
    if part_2:
        sams = set(find("SAM", grid, DIAGONALS))
        return (
            sum(
                map(
                    sams.__contains__,
                    chain.from_iterable(starmap(partial(x_complements, len("SAM")), sams)),
                )
            )
            // 2
        )
    else:
        return sum(1 for _ in find("XMAS", grid, DIRECTIONS))


_test_input = """
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_test_input), part_2=False) == 18
    assert run(f(_test_input), part_2=True) == 9
