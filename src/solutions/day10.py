from functools import partial
from typing import IO, Iterable

import util
from util import Grid, GridCoordinates, WeightedDiGraph


def incrementing_edges_graph(grid: Grid[int]) -> util.WeightedDiGraph[GridCoordinates]:
    get = util.indexer(grid)

    def diff(edge: tuple[GridCoordinates, GridCoordinates]) -> int:
        return get(edge[1]) - get(edge[0])

    graph = util.grid_to_graph(grid, diff)
    return {k: {h: 1 for h, w in edges.items() if w == 1} for k, edges in graph.items()}


def n_reachable_by_incrementing_paths(
    grid: util.Grid[int],
    graph: WeightedDiGraph[util.GridCoordinates],
    max_val: int,
    start: GridCoordinates,
) -> int:
    is_max = util.compose(util.indexer(grid), max_val.__eq__)
    return sum(1 for _ in filter(is_max, util.dfs_graph(graph, start)))


def n_incrementing_paths(
    grid: Grid[int],
    graph: WeightedDiGraph[GridCoordinates],
    max_val: int,
    start: GridCoordinates,
    acc: int = 1,
) -> int:
    value = util.index(grid, start)
    if value < max_val:
        rec = partial(n_incrementing_paths, grid, graph, max_val)
        return acc * sum(map(rec, graph.get(start, ())), 0)
    else:
        return int(value == max_val)


def parse(lines: Iterable[str]) -> util.Grid[int]:
    return list(map(util.compose(partial(map, int), list), map(str.strip, lines)))


def run(input: IO[str], part_2: bool = True) -> int:
    grid = parse(input)
    graph = incrementing_edges_graph(grid)
    starts = filter(util.compose(util.indexer(grid), (0).__eq__), graph)
    f = n_incrementing_paths if part_2 else n_reachable_by_incrementing_paths
    return sum(f(grid, graph, 9, start) for start in starts)


_test_input = """
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False), 36)
    util.assert_equal(run(f(_test_input), part_2=True), 81)
