import re
from functools import reduce
from itertools import chain, starmap
from operator import itemgetter, mul
from typing import IO, Iterable, Iterator, List, Literal, Tuple

HASH_SIZE = 256

HashValue = int
Label = str
FocalLength = int
LensSpec = Tuple[Label, FocalLength]
HashMap = List[List[LensSpec]]
Op = Literal["=", "-"]
Instruction = Tuple[Label, Op, FocalLength]
ADD: Op = "="
REMOVE: Op = "-"

instruction_re = re.compile(rf"(\w+)(?:([{REMOVE}])|([{ADD}])(\d+))")


def hash_step(acc: int, char: str) -> int:
    return ((acc + ord(char)) * 17) % HASH_SIZE


def hash_(s: Iterable[str]) -> int:
    return reduce(hash_step, s, 0)


def _op(box: List[LensSpec], inst: Instruction) -> List[LensSpec]:
    label, op, focal_len = inst
    ix = next((i for i, (label_, _) in enumerate(box) if label_ == label), None)
    if ix is None:
        if op == ADD:
            box.append((label, focal_len))
    else:
        if op == ADD:
            box[ix] = (label, focal_len)
        else:
            box.pop(ix)
    return box


def update(hashmap: HashMap, inst: Instruction) -> HashMap:
    label, op, focal_len = inst
    ix = hash_(label)
    box = hashmap[ix]
    hashmap[ix] = _op(box, inst)
    return hashmap


def focusing_power(box_ix: HashValue, box: List[LensSpec]) -> int:
    focal_lens = map(itemgetter(1), box)
    return (box_ix + 1) * sum(starmap(mul, enumerate(focal_lens, 1)))


def parse_instruction(s: str) -> Instruction:
    match = instruction_re.fullmatch(s)
    assert match
    label, remove, add, focal_len = match.groups()
    if add is None:
        assert remove == REMOVE
        return label, REMOVE, 0
    else:
        assert add == ADD
        return label, ADD, int(focal_len)


def parse(input: Iterable[str]) -> Iterator[str]:
    lines = map(str.strip, input)
    return chain.from_iterable(line.split(",") for line in lines)


def run(input: IO[str], part_2: bool = True) -> int:
    strings = parse(input)

    if part_2:
        instructions = map(parse_instruction, strings)
        hashmap: HashMap = reduce(update, instructions, [[] for _ in range(HASH_SIZE)])
        return sum(starmap(focusing_power, enumerate(hashmap)))
    else:
        return sum(map(hash_, strings))


_TEST_INPUT = """rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7"""


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 1320
    assert run(f(_TEST_INPUT), part_2=True) == 145
