from functools import partial
from itertools import chain, takewhile
from typing import IO, Iterable, Iterator

import util
from util import Grid, GridCoordinates, Predicate, T, Vector


def travel_until(
    grid: Grid[T], predicate: Predicate[GridCoordinates], vec: Vector, coords: GridCoordinates
) -> Iterator[GridCoordinates]:
    path = util.tail(util.iterate(partial(util.translate, vec), coords))
    return takewhile(util.invert(predicate), takewhile(util.bounds_check(grid), path))


def walk(
    grid: Grid[T], predicate: Predicate[GridCoordinates], start: GridCoordinates, vec: Vector
) -> Iterator[tuple[GridCoordinates, Vector]]:
    in_bounds = util.bounds_check(grid)
    while in_bounds(start):
        for coords in travel_until(grid, predicate, vec, start):
            yield coords, vec
            start = coords
        if not in_bounds(util.translate(vec, start)):
            break
        vec = (vec[1], -vec[0])  # turn right


def cycle_inducing_obstructions(
    grid: Grid[T],
    is_obstructed: util.Predicate[GridCoordinates],
    start: GridCoordinates,
    vec: Vector,
) -> Iterator[GridCoordinates]:
    visited = {start}
    prefix = [(start, vec)]
    for obstruction, direction in walk(grid, is_obstructed, start, vec):
        if obstruction not in visited:
            visited.add(obstruction)
            is_obstructed_ = util.any_(is_obstructed, obstruction.__eq__)
            path_ = chain(prefix, walk(grid, is_obstructed_, *prefix[-1]))
            if util.find_cycle(util.identity, path_) is not None:
                yield obstruction
        prefix.append((obstruction, direction))


def parse(lines: Iterable[str]) -> tuple[Grid[str], GridCoordinates, Vector]:
    grid = list(map(str.strip, lines))
    start = next(
        (i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if cell in "^>v<"
    )
    vec = {"^": (-1, 0), ">": (0, 1), "v": (1, 0), "<": (0, -1)}[util.index(grid, start)]
    return grid, start, vec


def run(input: IO[str], part_2: bool = True) -> int:
    grid, start, vec = parse(input)
    is_obstructed = util.compose(util.indexer(grid), "#".__eq__)
    if part_2:
        return sum(1 for _ in cycle_inducing_obstructions(grid, is_obstructed, start, vec))
    else:
        path = walk(grid, is_obstructed, start, vec)
        return len(set(chain([start], map(util.fst, path))))


_test_input = """
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False), 41)
    util.assert_equal(run(f(_test_input), part_2=True), 6)
