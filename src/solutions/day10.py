from functools import partial
from operator import add, mul
from typing import IO, Iterable

import util
from util import Grid, GridCoordinates, WeightedDiGraph


def incrementing_edges_graph(grid: Grid[int]) -> util.WeightedDiGraph[GridCoordinates]:
    def diff(edge: tuple[GridCoordinates, GridCoordinates]) -> int:
        return util.index(grid, edge[1]) - util.index(grid, edge[0])

    graph = util.grid_to_graph(grid, diff)
    return {k: {h: 1 for h, w in edges.items() if w == 1} for k, edges in graph.items()}


def n_reachable_by_incrementing_paths(
    grid: util.Grid[int],
    graph: WeightedDiGraph[util.GridCoordinates],
    max_val: int,
    start: GridCoordinates,
    all_paths: bool,
) -> int:
    is_max = util.compose(util.indexer(grid), max_val.__eq__)

    if all_paths:

        def node_value(node: GridCoordinates) -> int:
            return 1 if util.neighbors(graph, node) else is_max(node)

    else:
        node_value = is_max

    return util.dag_reduce(
        graph,
        node_value=node_value,
        edge_op=mul if all_paths else add,
        reduce_nbrs_op=sum,
        start=start,
        visited=None if all_paths else set(),
    )


def parse(lines: Iterable[str]) -> util.Grid[int]:
    return list(map(util.compose(partial(map, int), list), map(str.strip, lines)))


def run(input: IO[str], part_2: bool = True) -> int:
    grid = parse(input)
    graph = incrementing_edges_graph(grid)
    starts = filter(util.compose(util.indexer(grid), (0).__eq__), graph)
    f = partial(n_reachable_by_incrementing_paths, grid, graph, 9, all_paths=part_2)
    return sum(map(f, starts))


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
