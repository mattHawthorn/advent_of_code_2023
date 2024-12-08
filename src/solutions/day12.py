from collections import deque
from functools import partial
from itertools import chain
from typing import IO, Iterable, Iterator, Literal, NamedTuple, Sequence, cast

State = Literal["?", "#", "."]
UNKNOWN: State = "?"
ACTIVE: State = "#"
INACTIVE: State = "."


class Record(NamedTuple):
    states: Sequence[State]
    shape: Sequence[int]


def active_placements(states: Sequence[State], n_active: int) -> Iterator[int]:
    start = next((i for i, s in enumerate(states) if s != INACTIVE), None)
    if start is not None:
        prefix = states[start : start + n_active]  # noqa: E203
        if len(prefix) == n_active:
            window = deque(chain((INACTIVE,), prefix))
            for i, after in enumerate(
                chain(states[start + n_active :], (INACTIVE,)), start  # noqa: E203
            ):
                before = window.popleft()
                if before == ACTIVE:
                    break
                if after != ACTIVE and all(map(INACTIVE.__ne__, window)):
                    yield i
                window.append(after)


def possible_states(record: Record) -> int:
    def recurse(states: Sequence[State], shape: Sequence[int]):
        if not shape:
            yield 1
        elif sum(shape) + len(shape) - 1 <= len(states):
            n_active = shape[0]
            shape_tail = shape[1:]
            for offset in active_placements(states, n_active):
                yield from recurse(
                    states[offset + n_active + 1 :],  # noqa: E203
                    shape_tail,
                )

    return sum(recurse(record.states, record.shape))


def parse_record(line: str, concat: int = 1) -> Record:
    states, shape = line.split(maxsplit=1)
    return Record(
        cast(Sequence[State], states * concat),
        list(map(int, ",".join([shape] * concat).split(","))),
    )


def parse(input: Iterable[str], concat: int = 1) -> Iterator[Record]:
    return map(partial(parse_record, concat=concat), map(str.strip, input))


def run(input: IO[str], part_2: bool = True) -> int:
    records = list(parse(input, concat=5 if part_2 else 1))
    return sum(map(possible_states, records))


_TEST_INPUT = """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1""".strip()


def shape_of(states: str):
    import re

    return list(map(len, re.findall(rf"{ACTIVE}+", "".join(states))))


def naive_solve(record: Record):
    from itertools import combinations

    states, shape = record
    unknown = [i for i, s in enumerate(states) if s == UNKNOWN]
    active = [i for i, s in enumerate(states) if s == ACTIVE]
    total = sum(shape)
    for active_set in combinations(unknown, total - len(active)):
        solution = "".join(
            ACTIVE if s == ACTIVE or i in active_set else INACTIVE for i, s in enumerate(states)
        )
        if shape_of(solution) == shape:
            yield solution


def test():
    import io

    for record in map(
        parse_record,
        [
            "..???.. 1,1",
            "..???..? 3",
            "?.??#?...? 1,2,1",
            "?????????? 1,2,3",
            "????.######..#####. 1,6,5",
            "?.??????#??.???#.?? 1,1,2,1,4,1",
        ],
    ):
        assert sum(1 for _ in naive_solve(record)) == possible_states(record)

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 21
    assert run(f(_TEST_INPUT), part_2=True) == 525152
