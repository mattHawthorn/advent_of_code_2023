from functools import partial
from itertools import accumulate, chain, cycle
from operator import itemgetter, mul
from typing import IO, Iterable, Iterator, List, Literal, Optional, Sequence, Tuple

from util import Grid, find_cycle

Direction = Literal["U", "D", "L", "R"]

ROUND_ROCK = "O"
CUBE_ROCK = "#"
EMPTY = "."


def _tilt_seq_forward(seq: Sequence[str], i: int, j: int) -> Sequence[str]:
    n_round = seq[i:j].count(ROUND_ROCK)
    not_end = j < len(seq)
    return [EMPTY * (j - i - n_round), ROUND_ROCK * n_round, CUBE_ROCK * not_end]


def tilt_seq(forward: bool, seq: Sequence[str]) -> Sequence[str]:
    if forward:
        cube_pos = [i for i, s in enumerate(seq) if s == CUBE_ROCK]
        return "".join(
            chain.from_iterable(
                map(
                    partial(_tilt_seq_forward, seq),
                    chain((0,), map((1).__add__, cube_pos)),
                    chain(cube_pos, (len(seq),)),
                )
            )
        )
    else:
        return tilt_seq(True, seq[::-1])[::-1]


def tilt(grid: Grid[str], direction: Direction) -> Grid[str]:
    forward = direction in ("R", "D")
    tilt = partial(tilt_seq, forward)
    if direction in ("L", "R"):
        return list(map(tilt, grid))
    else:
        height = len(grid)
        width = len(grid[0])
        cols = (list(map(itemgetter(i), grid)) for i in range(width))
        new_cols = list(map(tilt, cols))
        return ["".join(map(itemgetter(i), new_cols)) for i in range(height)]


def tilt_iter(grid: Grid[str], directions: Iterable[Direction]) -> Iterator[Grid[str]]:
    return accumulate(directions, tilt, initial=grid)


def grid_key(grid_state: Tuple[Grid[str], Direction]) -> Tuple[str, Direction]:
    grid, direction = grid_state
    return "\n".join(map("".join, grid)), direction


def load(grid: Grid[str]) -> int:
    height = len(grid)
    row_counts = (row.count(ROUND_ROCK) for row in grid)
    return sum(map(mul, row_counts, range(height, 0, -1)))


def parse(input: Iterable[str]) -> Grid[str]:
    return list(map(str.strip, input))


def run(input: IO[str], part_2: bool = True, n: Optional[int] = None) -> int:
    grid = parse(input)

    n_iter = n if n is not None else (4_000_000_000 if part_2 else None)
    if n_iter is not None:
        directions: List[Direction] = ["U", "L", "D", "R"]
        grids = tilt_iter(grid, cycle(directions))
        states = zip(grids, cycle(directions))
        state_cycle = find_cycle(grid_key, states)
        final_grid, _ = state_cycle[n_iter]
        return load(final_grid)
    else:
        tilted_grid = tilt(grid, "U")
        return load(tilted_grid)


_TEST_INPUT = """
O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....""".strip()


def test():
    import io

    s = "#..O.##OO...##..O.."
    assert tilt_seq(True, s) == "#...O##...OO##....O"
    assert tilt_seq(False, s) == "#O...##OO...##O...."

    grid = parse(_TEST_INPUT.splitlines())
    n_round = sum(row.count(ROUND_ROCK) for row in grid)
    cube_pos = [[i for i, s in enumerate(row) if s == CUBE_ROCK] for row in grid]
    for direction in "U", "L", "D", "R":
        tilted = tilt(grid, direction)
        assert sum(row.count(ROUND_ROCK) for row in tilted) == n_round
        assert [[i for i, s in enumerate(row) if s == CUBE_ROCK] for row in tilted] == cube_pos

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 136
    assert run(f(_TEST_INPUT), part_2=True) == 64
