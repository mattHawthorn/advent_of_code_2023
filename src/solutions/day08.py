from functools import partial, reduce
from itertools import count, cycle, takewhile
from typing import IO, Iterable, Iterator, List, Literal, Mapping, Sequence, Tuple

from util import chunked, iterate, lcm

Node = str
Network = Mapping[Node, Tuple[Node, Node]]
Instruction = Literal[0, 1]
Congruence = int

SYMBOL_TO_INSTRUCTION: Mapping[str, Instruction] = {"L": 0, "R": 1}
START: Node = "AAA"
END: Node = "ZZZ"


def reduce_instructions(instructions: List[Instruction]) -> List[Instruction]:
    n_instructions = len(instructions)
    candidates = (instructions[:i] for i in range(1, n_instructions // 2 + 1))

    def is_repeating(candidate: List[Instruction]) -> bool:
        i = len(candidate)
        return n_instructions % i == 0 and all(
            chunk == candidate for chunk in chunked(i, instructions)
        )

    return next(filter(is_repeating, candidates), instructions)


def next_node(instructions: Iterator[Instruction], node_map: Network, node: Node) -> Node:
    direction = next(instructions)
    return node_map[node][direction]


def traverse(instructions: Iterator[Instruction], node_map: Network, node: Node) -> Iterator[Node]:
    return iterate(partial(next_node, instructions, node_map), node)


def find_cycle(
    instructions: Sequence[Instruction],
    node_map: Network,
    node: Node,
) -> Congruence:
    seen = {}
    n_instructions = len(instructions)
    for i, node in zip(count(0), traverse(cycle(instructions), node_map, node)):
        j = i % n_instructions
        if (j, node) in seen:
            return i - j
        else:
            seen[(j, node)] = i
    else:
        return i


def parse_node(s: str) -> Tuple[Node, Tuple[Node, Node]]:
    node, lr = map(str.strip, s.split("=", maxsplit=1))
    l, r = map(str.strip, lr.strip("()").split(",", maxsplit=1))
    return node, (l, r)


def parse_instructions(s: str) -> List[Instruction]:
    return list(map(SYMBOL_TO_INSTRUCTION.__getitem__, s))


def parse(input: Iterable[str]) -> Tuple[Sequence[Instruction], Network]:
    lines = map(str.strip, input)
    instructions = parse_instructions(next(lines))
    node_map = dict(map(parse_node, filter(bool, map(str.strip, lines))))
    return reduce_instructions(instructions), node_map


def run(input: IO[str], part_2: bool = True) -> int:
    instructions, node_map = parse(input)
    if part_2:

        def endswith(char: str, node: Node) -> bool:
            return node[-1] == char

        start_nodes = filter(partial(endswith, START[0]), node_map)
        is_end = partial(endswith, END[0])
        cycle_lens = map(partial(find_cycle, instructions, node_map, is_end), start_nodes)
        return reduce(lcm, cycle_lens)
    else:
        steps = takewhile(END.__ne__, traverse(cycle(instructions), node_map, START))
        return sum(1 for _ in steps)


_TEST_INPUT_1 = """
LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)""".strip()

_TEST_INPUT_2 = """
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT_1), part_2=False) == 6
    assert run(f(_TEST_INPUT_2), part_2=True) == 6
