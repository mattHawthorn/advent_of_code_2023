from functools import partial
from itertools import cycle
from typing import IO, Iterable

import util
from util import Grid, GridCoordinates, WeightedDiGraph


def perimeter(graph: WeightedDiGraph[GridCoordinates], component: set[GridCoordinates]):
    return 4 * len(component) - sum(map(len, map(partial(util.neighbors, graph), component)))


def cost1(graph: WeightedDiGraph[GridCoordinates], component: set[GridCoordinates]):
    return len(component) * perimeter(graph, component)


def n_corners(component: set[GridCoordinates], coords: GridCoordinates) -> int:
    is_nbr = component.__contains__
    is_nbr_adj = map(is_nbr, util.grid_neighbors(coords, diag=False))
    is_nbr_diag = map(is_nbr, util.grid_neighbors(coords, diag=True))
    return sum(
        (na1 and na2 and not nd) or (not na1 and not na2)
        for (na1, na2), nd in zip(util.window(2, cycle(is_nbr_adj)), is_nbr_diag)
    )


def number_of_sides(component: set[GridCoordinates]):
    corners = sum(map(partial(n_corners, component), component))
    return corners


def cost2(component: set[GridCoordinates]):
    return len(component) * number_of_sides(component)


def parse(input: Iterable[str]) -> tuple[Grid, WeightedDiGraph[GridCoordinates]]:
    grid = list(map(str.strip, input))
    value = util.indexer(grid)
    graph = {
        c1: {c2: 1 for c2 in neighbors if value(c1) == value(c2)}
        for c1, neighbors in util.grid_to_graph(grid, weight_fn=lambda _: 1).items()
    }
    return grid, graph


def run(input: IO[str], part_2: bool = True) -> int:
    global grid
    grid, graph = parse(input)
    components = util.connected_components(graph)
    cost = cost2 if part_2 else partial(cost1, graph)
    return sum(map(cost, components))


_test_input = """
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False), 1930)
    util.assert_equal(run(f(_test_input), part_2=True), 1206)
