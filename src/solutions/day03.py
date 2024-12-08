import re
from itertools import chain
from operator import mul
from typing import (
    IO,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    Match,
    NamedTuple,
    cast,
    get_args,
)

Op = Literal["mul", "do", "don't"]

_OPERATIONS: Mapping[Op, Callable[[int, int], int]] = {"mul": mul}


class Instruction(NamedTuple):
    op: Op
    args: tuple[int, ...]

    def __call__(self) -> int:
        return _OPERATIONS[self.op](*self.args)


_inst_re = re.compile(rf"({'|'.join(get_args(Op))})\((?:(\d+),(\d+))?\)")


def to_inst(match: Match[str]) -> Instruction:
    op = match.group(1)
    if op in _OPERATIONS:
        operands: tuple[int, ...] = (int(match.group(2)), int(match.group(3)))
    else:
        operands = ()
    return Instruction(cast(Op, op), operands)


def parse_line(line: str) -> Iterator[Instruction]:
    return map(to_inst, _inst_re.finditer(line))


def eval_arithmetic_instructions(instructions: Iterable[Instruction]) -> Iterator[int]:
    return (inst() for inst in instructions if inst.op in _OPERATIONS)


def eval_active_instructions(instructions: Iterable[Instruction]) -> Iterator[int]:
    enabled = True
    for inst in instructions:
        if inst.op == "do":
            enabled = True
        elif inst.op == "don't":
            enabled = False
        elif enabled:
            yield inst()


def run(input: IO[str], part_2: bool = True) -> int:
    instructions = list(chain.from_iterable(map(parse_line, map(str.strip, input))))
    values = (eval_active_instructions if part_2 else eval_arithmetic_instructions)(instructions)
    return sum(values)


_test_input = "xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))"


def test():
    import io

    f = io.StringIO
    assert run(f(_test_input), part_2=False) == 161
    assert run(f(_test_input), part_2=True) == 48
