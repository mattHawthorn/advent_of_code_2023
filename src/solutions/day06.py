from functools import reduce
from math import ceil, floor, sqrt
from operator import itemgetter, mul
from typing import IO, Iterable, List, Sequence, Tuple

ChargeTime = int
Distance = int
Record = Tuple[ChargeTime, Distance]


def winning_strategies(record: Record) -> Sequence[ChargeTime]:
    time, best_dist = record
    # solve (time - charge) * charge > best_dist for charge
    # charge^2 - charge*time + best_dist < 0
    b, c = -time, best_dist
    discriminant = sqrt(b**2 - 4 * c)
    int_discriminant = int(discriminant)
    is_int = float(int_discriminant) == discriminant and (int_discriminant % 2) == (b % 2)
    lo = (-discriminant - b) / 2
    hi = (discriminant - b) / 2
    return range(int(ceil(lo)) + is_int, int(floor(hi)) + 1 - is_int)


def parse(lines: Iterable[str]) -> List[Record]:
    lines = iter(lines)
    times = map(int, next(lines).split(":", 1)[1].split())
    distances = map(int, next(lines).split(":", 1)[1].split())
    return list(zip(times, distances))


def run(input: IO[str], part_2: bool = True) -> int:
    records = parse(input)
    if part_2:
        time = int("".join(map(str, map(itemgetter(0), records))))
        dist = int("".join(map(str, map(itemgetter(1), records))))
        return len(winning_strategies((time, dist)))
    else:
        strategies = map(winning_strategies, records)
        return reduce(mul, map(len, strategies))


_TEST_INPUT = """
Time:      7  15   30
Distance:  9  40  200
""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 288
    assert run(f(_TEST_INPUT), part_2=True) == 71503
