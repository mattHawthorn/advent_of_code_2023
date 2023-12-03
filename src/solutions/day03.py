from functools import partial, reduce
from itertools import chain, starmap, takewhile
from operator import mul
from typing import IO, Iterable, Iterator, List, Mapping, NamedTuple, Sequence

from util import Grid, GridCoordinates, adjacent_coords, invert_relation


class PartNumber(NamedTuple):
    coords: GridCoordinates
    length: int
    value: int


class Symbol(NamedTuple):
    coords: GridCoordinates
    value: str


def part_numbers_in_row(row_ix: int, row: Sequence[str], col_ix: int = 0) -> Iterator[PartNumber]:
    if col_ix < len(row):
        if row[col_ix].isdigit():
            digits = list(takewhile(str.isdigit, (row[i] for i in range(col_ix, len(row)))))
            yield PartNumber((row_ix, col_ix), len(digits), int("".join(digits)))
            yield from part_numbers_in_row(row_ix, row, col_ix + len(digits))
        else:
            yield from part_numbers_in_row(row_ix, row, col_ix + 1)


def part_numbers(grid: Grid[str]) -> Iterator[PartNumber]:
    return chain.from_iterable(starmap(part_numbers_in_row, enumerate(grid)))


def adjacent_symbols(grid: Grid, number: PartNumber) -> Iterator[Symbol]:
    width, height = len(grid[0]), len(grid)
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


def run(input: IO[str], part_2: bool = True) -> int:
    grid: Grid[str] = list(map(str.strip, input))
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
