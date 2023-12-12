from functools import partial
from itertools import combinations, product, starmap
from operator import itemgetter
from typing import IO, Iterable, Iterator, Sequence, Set

from util import Grid, GridCoordinates, compose, index, manhattan_distance

Space = str
GALAXY = "#"
EMPTY = "."


def row(grid: Grid[Space], i: int) -> Sequence[Space]:
    return grid[i]


def column(grid: Grid[Space], i: int) -> Iterable[Space]:
    return map(itemgetter(i), grid)


def is_empty(row_or_col: Iterable[Space]) -> bool:
    return all(map(EMPTY.__eq__, row_or_col))


def dist(
    empty_rows: Set[int],
    empty_cols: Set[int],
    expansion: int,
    coords1: GridCoordinates,
    coords2: GridCoordinates,
) -> int:
    initial_dist = manhattan_distance(coords1, coords2)
    y1, x1 = coords1
    y2, x2 = coords2
    extra_y_dist = sum(map(empty_rows.__contains__, range(min(y1, y2), max(y1, y2)))) * (
        expansion - 1
    )
    extra_x_dist = sum(map(empty_cols.__contains__, range(min(x1, x2), max(x1, x2)))) * (
        expansion - 1
    )
    return initial_dist + extra_x_dist + extra_y_dist


def galaxy_coords(space: Grid[Space]) -> Iterator[GridCoordinates]:
    return filter(
        compose(partial(index, space), GALAXY.__eq__),
        product(range(len(space)), range(len(space[0]))),
    )


def parse(input: Iterable[str]) -> Grid[Space]:
    return list(map(str.strip, input))


def run(input: IO[str], part_2: bool = True) -> int:
    space = parse(input)
    empty_rows = set(filter(compose(partial(row, space), is_empty), range(len(space))))
    empty_cols = set(filter(compose(partial(column, space), is_empty), range(len(space[0]))))
    distance = partial(dist, empty_rows, empty_cols, 1_000_000 if part_2 else 2)
    galaxies = galaxy_coords(space)
    galaxy_pairs = combinations(galaxies, 2)
    return sum(starmap(distance, galaxy_pairs))


_TEST_INPUT = """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 374
    # assert run(f(_TEST_INPUT), part_2=True) == 2
