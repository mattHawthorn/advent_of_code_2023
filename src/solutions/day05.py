import io
from functools import cmp_to_key, partial
from itertools import repeat
from typing import IO, Iterable, NamedTuple

from util import T, WeightedDiGraph, invert, parse_blocks, weighted_edges_to_graph


class Order(NamedTuple):
    before: int
    after: int


def parse_order(line: str) -> Order:
    before, after = map(int, line.strip().split("|"))
    return Order(before, after)


def parse_pages(line: str) -> list[int]:
    return list(map(int, line.split(",")))


def parse(input: Iterable[str]) -> tuple[list[Order], list[list[int]]]:
    orders, pages = parse_blocks(input, io.StringIO)
    return list(map(parse_order, orders)), list(map(parse_pages, pages))


def middle(arr: list[T]) -> T:
    return arr[len(arr) // 2]


def correctly_ordered(ordering: WeightedDiGraph[int], pages: list[int]) -> bool:
    pairs = zip(pages, pages[1:])
    return all(b in ordering.get(a, ()) for a, b in pairs)


def order_correctly(ordering: WeightedDiGraph[int], pages: list[int]) -> list[int]:
    def compare(a: int, b: int) -> int:
        if b in ordering.get(a, ()):
            return -1
        elif a in ordering.get(b, ()):
            return 1
        else:
            return 0

    return sorted(pages, key=cmp_to_key(compare))


def run(input: IO[str], part_2: bool = True) -> int:
    orders, pages = parse(input)
    index = weighted_edges_to_graph(zip(orders, repeat(1)))
    is_ordered = partial(correctly_ordered, index)
    if part_2:
        unordered = filter(invert(is_ordered), pages)
        ordered: Iterable[list[int]] = map(partial(order_correctly, index), unordered)
    else:
        ordered = filter(is_ordered, pages)

    return sum(map(middle, ordered))


_test_input = """
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_test_input), part_2=False) == 143
    assert run(f(_test_input), part_2=True) == 123
