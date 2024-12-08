from functools import partial
from itertools import chain, combinations, islice, product, starmap, takewhile
from typing import IO, Callable, Iterable, Iterator, Mapping

import util
from util import GridCoordinates


def parse(input: Iterable[str]) -> tuple[int, int, Mapping[str, list[GridCoordinates]]]:
    grid = list(map(str.strip, input))
    height, width = len(grid), len(grid[0])
    get = util.indexer(grid)
    nonempty = util.compose(get, ".".__ne__)
    return width, height, util.groupby(get, filter(nonempty, product(range(height), range(width))))


def antinodes(
    width: int,
    height: int,
    skip: int,
    n: int | None,
    a: GridCoordinates,
    b: GridCoordinates,
) -> Iterator[GridCoordinates]:
    x, y = a[0] - b[0], a[1] - b[1]
    in_bounds = partial(util.in_bounds, width, height)
    return chain.from_iterable(
        islice(
            takewhile(in_bounds, util.iterate(partial(util.translate, vec), start)),
            skip,
            None if n is None else skip + n,
        )
        for start, vec in [(a, (x, y)), (b, (-x, -y))]
    )


def all_antinodes(
    gen: Callable[[GridCoordinates, GridCoordinates], Iterable[GridCoordinates]],
    antennae: list[GridCoordinates],
) -> Iterator[GridCoordinates]:
    return chain.from_iterable(starmap(gen, combinations(antennae, 2)))


def all_antinodes_all_frequencies(
    gen: Callable[[GridCoordinates, GridCoordinates], Iterable[GridCoordinates]],
    antennae: Mapping[str, list[GridCoordinates]],
) -> Iterator[GridCoordinates]:
    return chain.from_iterable(map(partial(all_antinodes, gen), antennae.values()))


def run(input: IO[str], part_2: bool = True) -> int:
    width, height, antennae = parse(input)
    if part_2:
        gen_antinodes = partial(antinodes, width, height, 0, None)
    else:
        gen_antinodes = partial(antinodes, width, height, 1, 1)

    return sum(1 for _ in util.unique(all_antinodes_all_frequencies(gen_antinodes, antennae)))


_test_input = """
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False), 14)
    util.assert_equal(run(f(_test_input), part_2=True), 34)
