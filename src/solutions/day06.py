import bisect
from functools import partial
from itertools import chain, repeat, takewhile, tee
from operator import itemgetter
from typing import IO, Iterable, Iterator, Literal, NamedTuple, cast

import util
from util import Callable, Grid, GridCoordinates, Predicate, T

Direction = Literal["^", ">", "v", "<"]
State = tuple[GridCoordinates, Direction]

DIRECTIONS: tuple[Direction, ...] = ("^", ">", "v", "<")
VERTICAL_DIRECTIONS: tuple[Direction, ...] = ("^", "v")
INCREASING_DIRECTIONS: tuple[Direction, ...] = ("v", ">")


class GridIndex(NamedTuple):
    rows: list[list[int]]
    cols: list[list[int]]
    width: int
    height: int

    def with_(self, coords: GridCoordinates) -> "GridIndex":
        v, h = coords
        return GridIndex(
            [(insert(row, h) if i == v else row) for i, row in enumerate(self.rows)],
            [(insert(col, v) if j == h else col) for j, col in enumerate(self.cols)],
            self.width,
            self.height,
        )


def insert(row: list[int], i: int) -> list[int]:
    ix = bisect.bisect(row, i)
    if (ix > 0) and (row[ix - 1] == i):
        return row  # already present
    else:
        return list(chain.from_iterable((row[:ix], [i], row[ix:])))


def to_index(grid: Grid[T], predicate: Predicate[T]) -> GridIndex:
    return GridIndex(
        [[j for j, cell in enumerate(row) if predicate(cell)] for row in grid],
        [[i for i, row in enumerate(grid) if predicate(row[j])] for j in range(len(grid[0]))],
        len(grid[0]),
        len(grid),
    )


def next_state(
    next_direction: Callable[[Direction], Direction],
    index: GridIndex,
    state: State,
) -> State | None:
    (v, h), direction = state
    vertical = direction in VERTICAL_DIRECTIONS
    increasing = direction in INCREASING_DIRECTIONS
    decreasing = not increasing
    static_coord = h if vertical else v
    this_idx = (index.cols if vertical else index.rows)[static_coord]
    ix = bisect.bisect(this_idx, v if vertical else h)
    if (not this_idx) or (increasing and ix >= len(this_idx)) or (decreasing and ix <= 0):
        return None
    else:
        next_coord = this_idx[ix - decreasing] + (decreasing - increasing)
        next_coords = (next_coord, static_coord) if vertical else (static_coord, next_coord)
        return next_coords, next_direction(direction)


def visited_coords(
    width: int, height: int, state1: State, state2: State | None
) -> Iterator[GridCoordinates]:
    (v1, h1), dir1 = state1
    if state2 is None:
        hmin, hmax = -1, width
        vmin, vmax = -1, height
    else:
        (v2, h2), dir2 = state2
        hmin = hmax = h2
        vmin = vmax = v2

    increasing = dir1 in INCREASING_DIRECTIONS
    if dir1 in VERTICAL_DIRECTIONS:
        vs = range(v1, vmax) if increasing else range(v1, vmin, -1)
        hs = repeat(h1)
    else:
        hs = range(h1, hmax) if increasing else range(h1, hmin, -1)
        vs = repeat(v1)

    return zip(vs, hs)


def states_to_path(width: int, height: int, states: Iterable[State | None]) -> Iterator[State]:
    states1, states2 = tee(states, 2)
    next(states2)
    return chain.from_iterable(
        zip(visited_coords(width, height, s1, s2), repeat(s1[1]))
        for s1, s2 in zip(states1, states2)
        if s1 is not None
    )


def path(
    index: GridIndex,
    next_state: Callable[[GridIndex, State], State | None],
    start: State,
) -> Iterator[State]:
    next_state_ = partial(next_state, index)
    states = util.take_until(util.is_null, util.iterate(next_state_, start))
    return states_to_path(index.width, index.height, states)


def cycle_inducing_obstructions(
    index: GridIndex,
    next_state: Callable[[GridIndex, State], State | None],
    start: State,
) -> Iterator[GridCoordinates]:
    starts, path_ = tee(path(index, next_state, start), 2)
    next(path_)

    def induces_cycle(start_next: tuple[State, State]) -> bool:
        start, (obstruction, _) = start_next
        next_state_ = partial(next_state, index.with_(obstruction))
        states = util.take_until(util.is_null, util.iterate(next_state_, start))
        return util.find_cycle(util.identity, states) is not None

    def the_obstruction(start_next: tuple[State, State]) -> GridCoordinates:
        return start_next[1][0]

    return map(
        the_obstruction,
        filter(
            induces_cycle,
            util.unique_by(the_obstruction, zip(starts, takewhile(start.__ne__, path_))),
        ),
    )


def parse(lines: Iterable[str]) -> tuple[Grid[str], State]:
    grid = list(map(str.strip, lines))
    state = next(
        ((i, j), cast(Direction, cell))
        for i, row in enumerate(grid)
        for j, cell in enumerate(row)
        if cell in DIRECTIONS
    )
    return grid, state


def run(input: IO[str], part_2: bool = True) -> int:
    grid, state = parse(input)
    is_obstruction = "#".__eq__
    index = to_index(grid, is_obstruction)
    next_state_ = partial(next_state, lambda d: DIRECTIONS[(DIRECTIONS.index(d) + 1) % 4])
    if part_2:
        return sum(1 for _ in cycle_inducing_obstructions(index, next_state_, state))
    else:
        return len(set(map(itemgetter(0), path(index, next_state_, state))))


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
