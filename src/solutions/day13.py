import re
from typing import IO, Iterable, Iterator, NamedTuple

import util
from util import GridCoordinates

A_COST = 3
B_COST = 1

_line_re = re.compile(r"Button\s+(A|B):\s+X\+(\d+),\s+Y\+(\d+)", re.I)
_prize_re = re.compile(r"Prize:\s+X=(\d+),\s+Y=(\d+)", re.I)


class Machine(NamedTuple):
    a: GridCoordinates
    b: GridCoordinates
    prize: GridCoordinates


def solve(machine: Machine) -> GridCoordinates | None:
    ax, ay = machine.a
    bx, by = machine.b
    x, y = machine.prize
    det = ay * bx - ax * by
    rdet = ay * x - ax * y
    if det == 0:
        if rdet == 0:
            # collinear; 0 or infinite solutions
            sol = util.solve_linear_diophantine(ax, bx, x)
            if sol is None:
                print("COLNO", machine)
                return None
            else:
                gx, gy = sol.generator
                m_, n_ = sol.solution
                for z in m_ // gx, m_ // gy:
                    m, n = x - z * gx, y - z * gy
                    if m >= 0 and n >= 0:
                        print(ax * m + bx * n, x)
                        print(ay * m + by * n, y)
                        try:
                            assert x == ax * m + bx * n
                            assert y == ay * m + by * n
                        except:
                            breakpoint()
                        print("LIN", machine, m, n)
                        return m, n
                else:
                    print("LIN", machine)
                    return None
        else:
            print("DEG", machine)
            return None
    elif rdet % det == 0:
        # unique solution
        n = rdet // det
        m = (x - bx * n) // ax
        print(ax * m + bx * n, x)
        print(ay * m + by * n, y)
        try:
            assert x == ax * m + bx * n
            assert y == ay * m + by * n
        except:
            breakpoint()
        if m >= 0 and n >= 0:
            print("ONE    ", machine, m, n)
            return m, n
        else:
            # negative solution
            print(" NEG   ", machine, m, n)
            return None
    else:
        print("  NON  ", machine)
        return None


def cost_to_win(machine: Machine) -> int:
    solution = solve(machine)
    if solution is None:
        return 0
    else:
        return A_COST * solution[0] + B_COST * solution[1]


def parse_machine(text: str) -> Machine:
    a_line, b_line, prize_line = text.strip().splitlines()
    amatch = _line_re.match(a_line)
    bmatch = _line_re.match(b_line)
    prizematch = _prize_re.match(prize_line)
    if amatch.group(1).lower() != "a":
        amatch, bmatch = bmatch, amatch
    return Machine(
        a=(int(amatch.group(2)), int(amatch.group(3))),
        b=(int(bmatch.group(2)), int(bmatch.group(3))),
        prize=(int(prizematch.group(1)), int(prizematch.group(2))),
    )


def parse(input: Iterable[str]) -> Iterator[Machine]:
    return util.parse_blocks(input, parse_machine)


def run(input: IO[str], part_2: bool = True) -> int:
    machines = parse(input)
    if part_2:
        big = 10000000000000
        machines = (Machine(m.a, m.b, util.translate((big, big), m.prize)) for m in machines)
    return sum(map(cost_to_win, machines))


_test_input = """
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279

Button A: X+2, Y+4
Button B: X+1, Y+2
Prize: X=5, Y=10

Button A: X+12, Y+12
Button B: X+18, Y+18
Prize: X=19, Y=19

Button A: X+3, Y+6
Button B: X+5, Y+10
Prize: X=7, Y=14
""".strip()


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False), 485)
