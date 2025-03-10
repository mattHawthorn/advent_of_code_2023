from itertools import chain, repeat
from typing import IO, Collection, Iterable

import util
from util import Grid, GridCoordinates, WeightedDiGraph


def shortest_path(width: int, height: int, graph: WeightedDiGraph) -> list[GridCoordinates]:
    return util.djikstra(graph, (0, 0), (height, width))[0]


def parse(input: Iterable[str]) -> list[GridCoordinates]:
    return [(int(a), int(b)) for a, b in (line.strip().split(",") for line in input)]


def run(
    input: IO[str], part_2: bool = True, width: int = 70, height: int = 70, n_bytes: int = 1024
) -> int | str:
    bytes_ = list(map(util.swap, parse(input)))  # swap x, y for our usual convention
    head = bytes_[:n_bytes]
    occupied = set(head)
    grid: Grid[bool] = [[((i, j) in occupied) for j in range(width + 1)] for i in range(height + 1)]
    get = util.indexer(grid)
    graph = util.grid_to_graph(grid, lambda edge: (None if any(map(get, edge)) else 1))
    path = shortest_path(width, height, graph)

    if part_2:
        path_ = set(path)
        for i, c in enumerate(bytes_[n_bytes:], n_bytes):
            if c in path_:
                # obstruction; find a new shortest path
                graph.pop(c, None)
                path = shortest_path(width, height, graph)
                if not path:
                    if util.VERBOSE:
                        print(f"obstruction at {c}")
                        print(
                            util.render_grid(
                                [
                                    ["#."[(i, j) in graph] for j in range(width + 1)]
                                    for i in range(height + 1)
                                ],
                                labels=dict(chain(zip(path, repeat("+")), [(c, "O")])),
                            ),
                            end="\n",
                        )

                    return ",".join(map(str, reversed(c)))
                path_ = set(path)
        else:
            raise ValueError("no obstruction found")
    else:
        if util.VERBOSE:
            print(
                util.render_grid(
                    [["#."[(i, j) in graph] for j in range(width + 1)] for i in range(height + 1)],
                    labels=dict(chain(zip(path, repeat("+")))),
                ),
                end="\n",
            )

        return len(path) - 1


_TEST_INPUT = """
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_TEST_INPUT), part_2=False, width=6, height=6, n_bytes=12), 22)
    util.assert_equal(run(f(_TEST_INPUT), part_2=True, width=6, height=6, n_bytes=12), "6,1")
