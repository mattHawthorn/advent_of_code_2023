from functools import lru_cache, partial
from itertools import chain, filterfalse, takewhile
from operator import itemgetter
from typing import IO, Iterable, List, Literal, Sequence, Set, Tuple, cast

from util import GridCoordinates, in_bounds, index, iterate, translate

GridContents = Literal[".", "\\", "/", "|", "-"]
Mirror = Literal["\\", "/"]
Splitter = Literal["|", "-"]
Direction = Literal[0, 1, 2, 3]
BeamState = Tuple[GridCoordinates, Direction]

DIRECTIONS = U, L, D, R = [(-1, 0), (0, -1), (1, 0), (0, 1)]
EMPTY: GridContents = "."


class BeamGrid(List[Sequence[GridContents]]):
    def __hash__(self):
        return id(self)


def rotate(direction: Direction, by: int) -> Direction:
    return cast(Direction, (direction + by) % 4)


def reflect(direction: Direction, mirror: Mirror) -> Direction:
    vertical = direction % 2 == 0
    if mirror == "\\":
        step = 1 if vertical else -1
    else:
        step = -1 if vertical else 1
    return rotate(direction, step)


def split(direction: Direction, splitter: Splitter) -> List[Direction]:
    vertical = direction % 2 == 0
    if (splitter == "|" and vertical) or (splitter == "-" and not vertical):
        return [direction]
    else:
        return [rotate(direction, -1), rotate(direction, 1)]


@lru_cache(None)
def _step(grid: BeamGrid, state: BeamState) -> List[BeamState]:
    coords, direction = state
    contents = index(grid, coords)
    if contents == EMPTY:
        new_directions = [direction]
    elif contents == "\\" or contents == "/":
        new_directions = [reflect(direction, contents)]
    elif contents == "-" or contents == "|":
        new_directions = split(direction, contents)
    else:
        raise ValueError(contents)

    height = len(grid)
    width = len(grid[0])
    new_coords = (translate(coords, DIRECTIONS[d]) for d in new_directions)
    return [(c, d) for c, d in zip(new_coords, new_directions) if in_bounds(width, height, c)]


def step(grid: BeamGrid, prior_states: Set[BeamState], states: List[BeamState]) -> List[BeamState]:
    new_states = list(
        filterfalse(
            prior_states.__contains__, chain.from_iterable(map(partial(_step, grid), states))
        )
    )
    prior_states.update(new_states)
    return new_states


def num_energized(grid: BeamGrid, initial: BeamState) -> int:
    all_states = chain.from_iterable(
        takewhile(
            bool,
            iterate(partial(step, grid, set()), [initial]),
        )
    )
    return len(set(map(itemgetter(0), all_states)))


def parse(input: Iterable[str]) -> BeamGrid:
    return BeamGrid(map(partial(cast, GridContents), map(str.strip, input)))


def run(input: IO[str], part_2: bool = True) -> int:
    grid = parse(input)
    height = len(grid)
    width = len(grid[0])

    initial_states: Iterable[BeamState]
    if part_2:
        initial_states = chain(
            (((height - 1, i), 0) for i in range(width)),
            (((i, width - 1), 1) for i in range(height)),
            (((0, i), 2) for i in range(width)),
            (((i, 0), 3) for i in range(height)),
        )
    else:
        initial_states = [((0, 0), 3)]

    return max(map(partial(num_energized, grid), initial_states))


_TEST_INPUT = r"""
.|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|....""".strip()


def test():
    import io

    f = io.StringIO

    assert run(f(_TEST_INPUT), part_2=False) == 46
    assert run(f(_TEST_INPUT), part_2=True) == 51
