from functools import partial
from operator import add, mul
from typing import IO, Callable, Iterator, NamedTuple, Sequence

import util

Op = Callable[[int, int], int]


class UnsolvedExpr(NamedTuple):
    value: int
    operands: list[int]


def concat(a: int, b: int) -> int:
    return int(str(a) + str(b))


def solvable(all_ops: Sequence[Op], expr: UnsolvedExpr) -> bool:
    def inner(operands: util.LinkedList[int] | None, acc: int) -> bool:
        if not operands:
            return acc == expr.value
        elif acc <= expr.value:
            return any(inner(operands.tail, op(acc, operands.head)) for op in all_ops)
        else:
            return False

    return inner(util.LinkedList.from_iterable(util.tail(expr.operands)), expr.operands[0])


def parse_expr(line: str) -> UnsolvedExpr:
    value, operands = line.split(":", maxsplit=1)
    return UnsolvedExpr(int(value.strip()), list(map(int, operands.strip().split())))


def parse(input: IO[str]) -> Iterator[UnsolvedExpr]:
    return map(parse_expr, map(str.strip, input))


def run(input: IO[str], part_2: bool = True) -> int:
    inputs = parse(input)
    ops = (add, mul, concat) if part_2 else (add, mul)
    return sum(expr.value for expr in filter(partial(solvable, ops), inputs))


_test_input = """
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
""".strip()


def test():
    import io

    assert solvable((add, mul), UnsolvedExpr(913887, [3, 6, 7, 2, 752, 9, 5, 1, 36, 5, 2, 1]))

    f = io.StringIO
    assert run(f(_test_input), part_2=False) == 3749
    assert run(f(_test_input), part_2=True) == 11387
