from functools import partial
from itertools import accumulate, chain, islice, takewhile
from typing import IO, Collection, Iterable, Iterator, Literal, Mapping, NamedTuple, Sequence, cast

import util
from util import Grid, GridCoordinates, Vector

CoordSet = set[GridCoordinates]
Instr = Literal["^", "v", "<", ">"]
UD: Collection[Instr] = ("^", "v")
DIRECTIONS: Mapping[Instr, GridCoordinates] = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}


class GridState(NamedTuple):
    location: GridCoordinates
    walls: CoordSet
    boxes: CoordSet


def obstructing_boxes(
    box_width: int, boxes: CoordSet, loc: GridCoordinates, instr: Instr
) -> CoordSet:
    left = partial(util.translate, (0, -1))
    right = partial(util.translate, (0, 1))
    first = True

    def nbrs(loc: GridCoordinates) -> Iterator[GridCoordinates]:
        # util.print_("look left and right from", loc, "facing", instr)
        if instr in UD:
            lefts = islice(util.iterate(left, loc), box_width)
            return (
                lefts
                if first
                else chain(
                    lefts,
                    islice(util.iterate(right, loc), box_width),
                )
            )
        else:
            return iter((loc,))

    def next_front(dir_: Vector, front: CoordSet) -> CoordSet:
        front_ = map(partial(util.translate, dir_), front)
        if instr in UD:
            next_ = set(filter(boxes.__contains__, chain.from_iterable(map(nbrs, front_))))
            nonlocal first
            first = False
            return next_
        else:
            return set(filter(boxes.__contains__, front_))

    dir_ = DIRECTIONS[instr]
    # util.print_("looking", instr, "at", loc, "for boxes")
    if instr not in UD:
        dir_ = (dir_[0], dir_[1] * box_width)
        if instr == ">":
            loc = (loc[0], loc[1] - box_width + 1)
            # util.print_("actually start from", loc)
    # util.print_("look ahead by", dir_)
    fronts = takewhile(bool, util.iterate(partial(next_front, dir_), {loc}))
    return set(util.tail(chain.from_iterable(fronts)))


def step(box_width: int, state: GridState, instr: Instr) -> GridState:
    draw(box_width, state, instr)
    loc, walls, boxes = state
    dir_ = DIRECTIONS[instr]
    next_loc = util.translate(dir_, loc)
    boxes_ahead = obstructing_boxes(box_width, boxes, loc, instr)
    if not boxes_ahead:
        if next_loc in walls:
            # util.print_(instr, "at", loc, "no boxes; bumped wall at", next_loc)
            return state
        # util.print_(instr, "at", loc, "no boxes; proceed to", next_loc)
        return GridState(next_loc, walls, boxes)
    next_box_locs = set(map(partial(util.translate, dir_), boxes_ahead))
    check = chain.from_iterable(
        islice(util.iterate(partial(util.translate, (0, 1)), b), box_width) for b in next_box_locs
    )
    if any(map(walls.__contains__, check)):
        util.print_(boxes_ahead)
        # util.print_(instr, "at", loc, "boxes ahead hit wall")
        return state
    # util.print_(instr, "at", loc, "pushing boxes")
    boxes.difference_update(boxes_ahead)
    boxes.update(next_box_locs)
    return GridState(next_loc, walls, boxes)


def simulate(box_width: int, state: GridState, instrs: Sequence[Instr]) -> Iterator[GridState]:
    return accumulate(instrs, partial(step, box_width), initial=state)


def gps(coords: GridCoordinates) -> int:
    y, x = coords
    return y * 100 + x


def parse(input: Iterable[str], box_width: int) -> tuple[GridState, Sequence[Instr]]:
    grid_block, instr_block = util.parse_blocks(input, util.identity)
    grid_block = (
        grid_block.replace("#", "#" * box_width)
        .replace(".", "." * box_width)
        .replace("@", "@" + "." * (box_width - 1))
        .replace("O", "O" + "." * (box_width - 1))
    )
    util.print_("initial grid:")
    util.print_(grid_block, end="\n\n")
    grid = list(map(str.strip, grid_block.strip().splitlines()))
    global width, height
    width, height = len(grid[0]), len(grid)

    def locations_of(grid: Grid, char: str) -> CoordSet:
        return {(i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if cell == char}

    walls = locations_of(grid, "#")
    boxes = locations_of(grid, "O")
    location = next(iter(locations_of(grid, "@")))
    instrs = "".join(instr_block.strip().split())
    return GridState(location, walls, boxes), cast(Sequence[Instr], instrs)


# globals used by `draw`
width: int
height: int
step_: int = 0
min_step: int = 186


def draw(box_width, state, instr):
    global step_, min_step, width, height
    step_ += 1
    loc, walls, boxes = state
    grid = "\n".join(
        "".join(
            (
                "#"
                if (i, j) in walls
                else ("O" if (box_width == 1) else ("[" + "-" * (box_width - 2) + "]"))
                if ((i, j) in boxes)
                else ("@")
                if ((i, j) == loc)
                else ("." if not any((i, j - k) in state.boxes for k in range(box_width)) else "")
            )
            for j in range(width)
        )
        for i in range(height)
    )
    if step_ >= min_step:
        util.print_()
        util.print_("move", instr, "from", loc, "step", step_, "at state:")
        util.print_(grid, end="\n\n")


def run(input: IO[str], part_2: bool = True, show_after: int = 0) -> int:
    global min_step
    min_step = show_after
    box_width = 1 + part_2
    state, instrs = parse(input, box_width)
    final_state = util.last(simulate(box_width, state, instrs))
    draw(box_width, final_state, "final")
    return sum(map(gps, final_state.boxes))


_TEST_INPUT = """
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_TEST_INPUT), part_2=False), 10092)
    util.assert_equal(run(f(_TEST_INPUT), part_2=True), 9021)
