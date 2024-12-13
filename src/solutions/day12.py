from functools import partial
from itertools import chain, cycle, filterfalse, islice
from typing import IO, Iterable

import util
from util import Grid, GridCoordinates, WeightedDiGraph


def parse(input: Iterable[str]) -> tuple[Grid, WeightedDiGraph[GridCoordinates]]:
    grid = list(map(str.strip, input))
    graph = util.grid_to_graph(grid, weight_fn=lambda _: 1)
    value = util.indexer(grid)
    region_graph = {
        c1: {c2: 1 for c2 in neighbors if value(c1) == value(c2)} for c1, neighbors in graph.items()
    }
    return grid, region_graph


def perimeter(graph: WeightedDiGraph[GridCoordinates], component: set[GridCoordinates]):
    return 4 * len(component) - sum(map(len, map(partial(util.neighbors, graph), component)))


def cost1(graph: WeightedDiGraph[GridCoordinates], component: set[GridCoordinates]):
    return len(component) * perimeter(graph, component)


def is_exterior(graph: WeightedDiGraph[GridCoordinates], coords: GridCoordinates):
    return len(util.neighbors(graph, coords)) < 4


def n_corners(component: set[GridCoordinates], is_interior: bool, coords: GridCoordinates) -> int:
    is_nbr = util.invert(component.__contains__) if is_interior else component.__contains__
    membership = list(map(is_nbr, util.grid_neighbors(coords)))
    nbrs = islice(cycle(membership), 1, None)
    return sum(map((2).__eq__, map(sum, zip(membership, nbrs))))


def number_of_sides(graph: WeightedDiGraph[GridCoordinates], component: set[GridCoordinates]):
    boundary_nodes = list(filter(partial(is_exterior, graph), component))
    exterior_nodes = set(
        filterfalse(
            component.__contains__, chain.from_iterable(map(util.grid_neighbors, boundary_nodes))
        )
    )
    interior_corners = sum(map(partial(n_corners, component, True), boundary_nodes))
    exterior_corners = sum(map(partial(n_corners, component, False), exterior_nodes))
    return interior_corners + exterior_corners


def cost2(graph, component: set[GridCoordinates]):
    return len(component) * number_of_sides(graph, component)


def run(input: IO[str], part_2: bool = True) -> int:
    grid, graph = parse(input)
    components = util.connected_components(graph)
    cost = cost2 if part_2 else cost1
    return sum(map(partial(cost, graph), components))


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
