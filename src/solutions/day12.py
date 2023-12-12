from collections import deque
from itertools import chain
from typing import IO, Iterable, Iterator, Literal, NamedTuple, Sequence, cast

State = Literal["?", "#", "."]
UNKNOWN: State = "?"
OPERATIONAL: State = "#"
INACTIVE: State = "."


class Record(NamedTuple):
    states: Sequence[State]
    shape: Sequence[int]


def active_placements(states: Sequence[State], n_active: int) -> Iterator[int]:
    if len(states) >= n_active:
        window = deque(chain((INACTIVE,), states[:n_active]))
        for i, after in enumerate(chain(states[n_active:], (INACTIVE,))):
            before = window.popleft()
            if (
                before in (INACTIVE, UNKNOWN)
                and after in (INACTIVE, UNKNOWN)
                and all(map((UNKNOWN, OPERATIONAL).__contains__, window))
            ):
                yield i
            window.append(after)


def possible_states(record: Record) -> int:
    def recurse(states: Sequence[State], shape: Sequence[int], prev=()):
        if not shape:
            yield 1
        elif sum(shape) + len(shape) - 1 <= len(states):
            n_active = shape[0]
            shape_tail = shape[1:]
            for offset in active_placements(states, n_active):
                yield from recurse(states[offset + n_active + 1 :], shape_tail)  # noqa: E203

    return sum(recurse(record.states, record.shape))


def parse_record(line: str) -> Record:
    states, shape = line.split(maxsplit=1)
    return Record(cast(Sequence[State], states.strip(INACTIVE)), list(map(int, shape.split(","))))


def parse(input: Iterable[str]) -> Iterator[Record]:
    return map(parse_record, map(str.strip, input))


def run(input: IO[str], part_2: bool = True) -> int:
    records = list(parse(input))
    return sum(map(possible_states, records))


_TEST_INPUT = """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 21
    # assert run(f(_TEST_INPUT), part_2=True) == 2
