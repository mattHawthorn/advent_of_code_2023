from functools import partial
from itertools import chain, filterfalse, product, takewhile
from operator import itemgetter
from typing import IO, Callable, Dict, Iterable, Iterator, Mapping, Set, Tuple

from util import Grid, GridCoordinates, adjacent_coords, any_, compose, index, iterate, translate

Tile = str
GridStep = Tuple[GridCoordinates, GridCoordinates]
PathTransitions = Mapping[GridCoordinates, GridCoordinates]

START: Tile = "S"
U: GridCoordinates = (-1, 0)
D: GridCoordinates = (1, 0)
L: GridCoordinates = (0, -1)
R: GridCoordinates = (0, 1)
UL: GridCoordinates = (-1, -1)
DR: GridCoordinates = (1, 1)

STEPS: Dict[Tile, GridStep] = {
    "|": (U, D),
    "-": (L, R),
    "L": (R, U),
    "J": (L, U),
    "7": (L, D),
    "F": (R, D),
}


def find_start(grid: Grid[Tile]) -> GridCoordinates:
    return next(
        (i, j) for i, j in product(range(len(grid)), range(len(grid[0]))) if grid[i][j] == START
    )


def step(grid: Grid[str], step: GridStep) -> GridStep:
    prior_coords, coords = step
    tile = index(grid, coords)
    steps = STEPS[tile]
    next_coords = next(filter(prior_coords.__ne__, map(partial(translate, coords), steps)))
    return coords, next_coords


def is_adjacent(grid: Grid, coords1: GridCoordinates, coords2: GridCoordinates) -> bool:
    tile = index(grid, coords2)
    steps = STEPS.get(tile, ())
    return any(map(coords1.__eq__, map(partial(translate, coords2), steps)))


def traverse(
    grid: Grid, start: GridCoordinates, next: GridCoordinates
) -> Iterator[GridCoordinates]:
    steps = iterate(partial(step, grid), (start, next))
    coords = map(itemgetter(1), steps)
    return chain((start,), takewhile(start.__ne__, coords))


def half_grid_neighbors(
    boundary: PathTransitions, half_grid_coords: GridCoordinates
) -> Iterator[GridCoordinates]:
    # grid neighbors of a half-grid point without passing through the boundary
    grid_neighbors_ = list(map(partial(translate, half_grid_coords), (U, UL, L)))
    for nbr1, nbr2, step in zip(
        chain((half_grid_coords,), grid_neighbors_),
        chain(grid_neighbors_, (half_grid_coords,)),
        (R, U, L, D),
    ):
        if boundary.get(nbr1) != nbr2 and boundary.get(nbr2) != nbr1:
            yield translate(half_grid_coords, step)


def half_grid_shell(
    boundary: PathTransitions, seeds: Set[GridCoordinates]
) -> Iterator[GridCoordinates]:
    return chain.from_iterable(map(partial(half_grid_neighbors, boundary), seeds))


def boundary_condition(width: int, height: int) -> Callable[[GridCoordinates], bool]:
    return any_(
        compose(itemgetter(0), (0).__gt__),
        compose(itemgetter(1), (0).__gt__),
        compose(itemgetter(0), height.__le__),
        compose(itemgetter(1), width.__le__),
    )


def reachable_half_grid_points(
    grid: Grid[str], boundary: PathTransitions, half_grid_seed: GridCoordinates
) -> Set[GridCoordinates]:
    boundary_condition_ = boundary_condition(len(grid[0]) + 1, len(grid) + 1)
    prior_coords: Set[GridCoordinates] = set()

    def next_shell(prior_shell: Set[GridCoordinates]):
        shell = set(half_grid_shell(boundary, prior_shell))
        shell = set(filterfalse(any_(prior_coords.__contains__, boundary_condition_), shell))
        prior_coords.update(shell)
        return shell

    shells = takewhile(bool, iterate(next_shell, {half_grid_seed}))
    return set(chain.from_iterable(shells))


def reachable_regions(grid: Grid[str], boundary: PathTransitions, visited: Set[GridCoordinates]):
    height, width = len(grid), len(grid[0])
    next_seeds = filterfalse(visited.__contains__, product(range(height), range(width)))
    while next_seed := next(next_seeds, None):
        region = reachable_half_grid_points(grid, boundary, next_seed)
        visited.update(region)
        yield region


def num_grid_points(half_grid_coords: Set[GridCoordinates]) -> int:
    def is_grid_point(coords: GridCoordinates) -> bool:
        return all(
            map(compose(partial(translate, coords), half_grid_coords.__contains__), (R, D, DR))
        )

    return sum(1 for _ in filter(is_grid_point, half_grid_coords))


def parse(lines: Iterable[str]) -> Grid[Tile]:
    return list(map(str.strip, lines))


def to_transition_map(loop: Iterable[GridCoordinates]) -> PathTransitions:
    loop_ = list(loop)
    return dict(zip(loop_, chain(loop_[1:], loop_[:1])))


def run(input: IO[str], part_2: bool = True) -> int:
    grid = parse(input)
    start = find_start(grid)
    first = next(
        filter(
            partial(is_adjacent, grid, start),
            adjacent_coords(start, len(grid[0]), len(grid[1])),
        )
    )
    loop = traverse(grid, start, first)
    if part_2:
        transitions = to_transition_map(loop)
        # (0, 0) is the first half-grid seed coordinate and is always on the outside;
        # furthermore, there are only 2 regions in the half-grid: inside and outside.
        outside, inside = reachable_regions(grid, transitions, set())
        return num_grid_points(inside)
    else:
        len_ = sum(1 for _ in loop)
        return len_ // 2


_TEST_INPUT_1 = """
..F7.
.FJ|.
SJ.L7
|F--J
LJ...""".strip()

_TEST_INPUT_2 = """
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJIF7FJ-
L---JF-JLJIIIIFJLJJ7
|F|F-JF---7IIIL7L|7|
|FFJF7L7F-JF7IIL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT_1), part_2=False) == 8
    assert run(f(_TEST_INPUT_2), part_2=True) == 10
