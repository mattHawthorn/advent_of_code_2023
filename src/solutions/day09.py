from fractions import Fraction
from functools import partial, reduce
from itertools import repeat, takewhile
from numbers import Rational
from operator import mul, sub
from typing import IO, List, Tuple, TypeVar

from util import iterate

N = TypeVar("N", bound=Rational)
Series = List[int]
Polynomial = List[N]
Vector = List[N]
Matrix = List[Vector[N]]
LinearSystem = Tuple[Matrix[N], Vector[N]]


def diff(series: Series) -> Series:
    return [b - a for a, b in zip(series[1:], series)]


def multiply(vec: Vector[N], n: N) -> Vector[N]:
    return list(map(n.__mul__, vec))


def subtract(vec1: Vector[N], vec2: Vector[N]) -> Vector[N]:
    return list(map(sub, vec1, vec2))


def row_reduce(X_y: LinearSystem, col_ix: int, backward: bool = False) -> LinearSystem:
    X, y = X_y
    denom = X[col_ix][col_ix]
    X[col_ix] = new_row = [Fraction(n, denom) for n in X[col_ix]]
    y[col_ix] = Fraction(y[col_ix], denom)
    for i in range(col_ix - 1, -1, -1) if backward else range(col_ix + 1, len(X)):
        multiplier = X[i][col_ix]
        X[i] = subtract(X[i], multiply(new_row, multiplier))
        y[i] = y[i] - y[col_ix] * multiplier
    return X, y


def solve_linear(X: Matrix, y: Vector) -> LinearSystem:
    X, y = reduce(row_reduce, range(len(X)), (X, y))
    X, y = reduce(partial(row_reduce, backward=True), range(len(X) - 1, -1, -1), (X, y))
    return X, y


def polynomial_degree(series: Series) -> int:
    nonzero = any
    diffs = takewhile(nonzero, iterate(diff, series))
    return sum(1 for _ in diffs)


def solve_polynomial(series: Series) -> Polynomial[Fraction]:
    degree = polynomial_degree(series)
    matrix: Matrix[Fraction] = list(
        map(list, (map(n.__pow__, range(degree)) for n in map(Fraction, range(degree))))
    )
    return solve_linear(matrix, list(map(Fraction, series[:degree])))[1]


def evaluate(poly: Polynomial[N], n: int) -> N:
    powers = map(n.__pow__, range(len(poly)))
    return sum(map(mul, poly, powers))


def parse_series(line: str) -> Series:
    return list(map(int, line.strip().split()))


def run(input: IO[str], part_2: bool = True) -> int:
    series = list(map(parse_series, input))
    polys = map(solve_polynomial, series)
    xs = repeat(-1, len(series)) if part_2 else map(len, series)
    ys = map(evaluate, polys, xs)
    return int(sum(ys))


_TEST_INPUT = """
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 114
    assert run(f(_TEST_INPUT), part_2=True) == 2
