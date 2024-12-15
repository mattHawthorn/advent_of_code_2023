import re
from collections import Counter
from functools import partial, reduce
from itertools import filterfalse, islice
from operator import is_, mul
from typing import IO, Iterable, Iterator, NamedTuple

import util
from util import GridCoordinates

_line_re = re.compile(r"p=(-?\d+),(-?\d+)\s+v=(-?\d+),(-?\d+)")


class Robot(NamedTuple):
    position: GridCoordinates
    velocity: GridCoordinates


def location_at(width: int, height: int, time: int, robot: Robot):
    x, y = robot.position
    vx, vy = robot.velocity
    return (x + vx * time) % width, (y + vy * time) % height


def quadrant(width: int, height: int, position: GridCoordinates) -> int | None:
    x, y = position
    mx = width // 2
    my = height // 2
    if x == mx or y == my:
        return None
    up = x < mx
    left = y < my
    return 2 * up + left


def parse(input: Iterable[str]) -> Iterator[Robot]:
    matches = map(_line_re.fullmatch, map(str.strip, input))
    return (
        Robot((int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4))))
        for m in matches
    )


def run(input_: IO[str], part_2: bool = True, width: int = 101, height: int = 103) -> int:
    robots = list(parse(input_))
    if part_2:

        def next_(robots_: list[Robot]) -> list[Robot]:
            return [Robot(location_at(width, height, 1, r), r.velocity) for r in robots_]

        states = islice(util.iterate(next_, robots), 10000)
        for i, state in enumerate(states):
            coords = set(r.position for r in state)
            g = util.edges_to_graph_with_weight(
                lambda *a: 1,
                (
                    (c1, c2)
                    for c1, c2 in util.window(2, sorted(coords))
                    if util.manhattan_distance(c1, c2) == 1
                ),
            )
            largest = max(map(len, util.connected_components(g)))
            if largest > 10:
                print_locations(width, height, coords)
                print(i, "largest component", largest, "out of", len(robots))
                return i
    else:
        steps = 100
        final_positions = map(partial(location_at, width, height, steps), robots)
        qcounts = Counter(
            filterfalse(partial(is_, None), map(partial(quadrant, width, height), final_positions))
        )
        return reduce(mul, qcounts.values(), 1)


def print_locations(width, height, coords):
    print(
        "\n".join(
            "".join("#" if (i, j) in coords else "." for i in range(width)) for j in range(height)
        )
    )


_test_input = """
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False, width=11, height=7), 12)
