from functools import partial
from itertools import chain, cycle, islice, product, repeat
from operator import itemgetter
from typing import IO, Iterable

import util
from util import Grid, GridCoordinates, Vector

State = tuple[GridCoordinates, Vector]


def to_maze_graph(step_cost: int, turn_cost: int, grid: Grid[str]):
    get = util.indexer(grid)
    is_wall = "#".__eq__
    grid_graph: util.WeightedDiGraph[GridCoordinates] = util.grid_to_graph(
        grid,
        weight_fn=lambda edge: (None if any(map(util.compose(get, is_wall), edge)) else 1),
    )
    state_graph: util.WeightedDiGraph[State] = util.weighted_edges_to_graph(
        chain(
            (
                (((a, dir_ := util.translate_inv(a, b)), (b, dir_)), step_cost)
                for (a, b), _ in util.all_edges(grid_graph)
            ),
            chain.from_iterable(
                zip(
                    (
                        ((a, d1), (a, d2))
                        for d1, d2 in chain(
                            islice(util.window(2, cycle(util.RDLU)), 1, 5),
                            islice(util.window(2, cycle(reversed(util.RDLU))), 1, 5),
                        )
                    ),
                    repeat(turn_cost),
                )
                for a, neighbors in grid_graph.items()
                if len(neighbors) == 1
                # nodes that are either a dead end
                or len(dirs := list(map(partial(util.translate_inv, a), neighbors))) > 1
                and any(len(set(map(util.compose(f, abs), dirs))) > 1 for f in (util.fst, util.snd))
                # or sit at a right-angle turn
            ),
        )
    )
    return grid_graph, state_graph


def run(input: IO[str], part_2: bool = True) -> int:
    grid: Grid[str] = list(map(str.strip, input))
    grid_graph, graph = to_maze_graph(1, 1000, grid)
    get = util.indexer(grid)
    start = next(
        (c, d) for c, d in graph if get(c) == "S" and d == (0, 1)
    )  # start facing east at S
    ends = {(c, d) for c, d in graph if get(c) == "E"}  # end at E facing any direction
    solution = util.djikstra_any(graph, start, ends)
    assert solution is not None
    path, score = solution

    if part_2:
        forward = util.DjikstraState(graph, start, ends)
        backwards = [util.DjikstraState(graph, end, start.__eq__) for end in ends]

        def is_on_shortest_paths(node: State) -> int:
            coords, dir_ = node
            reverse_dir = (-1 * dir_[0], -1 * dir_[1])
            return (
                forward.distance(node)
                + min(backward.distance((coords, reverse_dir)) for backward in backwards)
                <= score
            )

        nodes = set(map(itemgetter(0), filter(is_on_shortest_paths, graph)))
        result = len(nodes)
    else:
        nodes = set()
        result = score

    if util.VERBOSE:
        print(
            util.render_grid(
                grid,
                {c: "O" for c in nodes}
                if part_2
                else {c: ">v<^"[util.RDLU.index(d)] for c, d in path},
            )
        )

    return result


_TEST_INPUT = r"""
#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################""".strip()


def test():
    import io

    f = io.StringIO

    util.assert_equal(run(f(_TEST_INPUT), part_2=False), 11048)
    util.assert_equal(run(f(_TEST_INPUT), part_2=True), 64)
