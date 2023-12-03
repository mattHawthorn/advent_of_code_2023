from functools import reduce
from operator import mul
from typing import IO, Iterable, Iterator, List, Mapping, NamedTuple

from returns.curry import partial

from util import Grid, GridCoordinates, adjacent_coords, invert_relation


class PartNumber(NamedTuple):
    coords: GridCoordinates
    length: int
    value: int


class Symbol(NamedTuple):
    coords: GridCoordinates
    value: str


def part_numbers(grid: Grid[str]) -> Iterator[PartNumber]:
    for i, row in enumerate(grid):
        num = []
        for j, s in enumerate(row):
            if s.isdigit():
                num.append(s)
            elif num:
                yield PartNumber((i, j - len(num)), len(num), int("".join(num)))
                num = []
        if num:
            yield PartNumber((i, j + 1 - len(num)), len(num), int("".join(num)))


def adjacent_symbols(grid: Grid, number: PartNumber) -> Iterator[Symbol]:
    width = len(grid[0])
    height = len(grid)
    return (
        Symbol((m, n), symbol)
        for m, n in adjacent_coords(number.coords, width, height, number.length)
        if (symbol := grid[m][n]) != "."
    )


def adjacent_to_symbol(grid: Grid, number: PartNumber) -> bool:
    return next(adjacent_symbols(grid, number), None) is not None


def adjacent_gears(grid: Grid, number: PartNumber) -> Iterator[Symbol]:
    return filter(lambda sym: sym.value == "*", adjacent_symbols(grid, number))


def gear_number_adjacency(
    grid: Grid, numbers: Iterable[PartNumber]
) -> Mapping[Symbol, List[PartNumber]]:
    number_to_gears = {number: adjacent_gears(grid, number) for number in numbers}
    return {
        gear: numbers
        for gear, numbers in invert_relation(number_to_gears).items()
        if len(numbers) == 2
    }


def gear_ratio(numbers: Iterable[PartNumber]) -> int:
    return reduce(mul, (n.value for n in numbers))


def parse(input: Iterable[str]) -> Grid[str]:
    return list(map(list, map(str.strip, input)))


def run(input: IO[str], part_2: bool = True) -> int:
    grid = parse(input)
    numbers = part_numbers(grid)
    if part_2:
        gear_to_numbers = gear_number_adjacency(grid, numbers)
        return sum(map(gear_ratio, gear_to_numbers.values()))
    else:
        valid_numbers = filter(partial(adjacent_to_symbol, grid), numbers)
        return sum(n.value for n in valid_numbers)


_TEST_INPUT = """
467..114..
...*......
..35..633.
......#...
617*......
.....+..58
..592.....
......755.
...$..*...
.664...598""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 4361
    assert run(f(_TEST_INPUT), part_2=True) == 467835
