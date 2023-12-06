from bisect import bisect_right
from functools import partial, reduce
from itertools import chain, takewhile
from typing import IO, Iterable, Iterator, List, Tuple

from util import chunked, iterate, parse_blocks

ID = int
IDRange = range
MapRange = Tuple[IDRange, IDRange]
Category = str


class Map:
    def __init__(self, source: Category, target: Category, ranges: Iterable[MapRange]):
        self.source = source
        self.target = target
        self.ranges = sorted(ranges, key=lambda r: r[0].start)
        self.starts = [range[0].start for range in self.ranges]

    def __bool__(self):
        return bool(self.ranges)

    def __call__(self, item: ID):
        ix = bisect_right(self.starts, item) - 1
        if ix < 0:
            return item
        else:
            source_range, target_range = self.ranges[ix]
            return target_range[source_range.index(item)] if item in source_range else item


def fill_ranges(map_ranges: Iterable[MapRange], min_: int, max_: int) -> List[MapRange]:
    """Ensure the domain of a function defined by mapped ranges is total.
    Results are sorted by range start"""
    by_endpoint = sorted(map_ranges, key=lambda r: r[0].start)
    if by_endpoint:
        first = by_endpoint[0][0]
        last = by_endpoint[-1][0]
        return [
            map_range
            for map_range in chain(
                [(range(min_, first.start), range(min_, first.start))],
                chain.from_iterable(
                    [
                        (input, output),
                        (range(input.stop, next_input.start), range(input.stop, next_input.start)),
                    ]
                    for (input, output), (next_input, _) in zip(by_endpoint, by_endpoint[1:])
                ),
                [by_endpoint[-1], (range(last.stop, max_), range(last.stop, max_))],
            )
            if map_range[0]
        ]
    else:
        return [(range(min_, max_), range(min_, max_))]


def ranges_overlap(output1: IDRange, range2: MapRange) -> bool:
    input2, _ = range2
    return (
        (input2.start <= output1.start < input2.stop)
        or (input2.start < output1.stop <= input2.stop)
        or (output1.start <= input2.start < output1.stop)
    )


def overlapping_ranges(map_range: MapRange, ranges: Iterable[MapRange]) -> Iterable[MapRange]:
    """Assumes `ranges` is sorted and total as in the output of `fill_ranges`"""
    return filter(partial(ranges_overlap, map_range[1]), ranges)


def intersect_ranges(map_range1: MapRange, map_range2: MapRange) -> MapRange:
    input1, output1 = map_range1
    input2, output2 = map_range2
    start = max(output1.start, input2.start)
    stop = min(output1.stop, input2.stop) - 1
    new_output = range(output2[input2.index(start)], output2[input2.index(stop)] + 1)
    new_input = range(input1[output1.index(start)], input1[output1.index(stop)] + 1)
    return new_input, new_output


def compose_range(ranges: Iterable[MapRange], map_range: MapRange) -> Iterable[MapRange]:
    return map(partial(intersect_ranges, map_range), overlapping_ranges(map_range, ranges))


def compose_ranges(
    ranges1: Iterable[MapRange], ranges2: Iterable[MapRange], fill_input: bool = True
) -> Iterable[MapRange]:
    min_ = min(input.start for input, _ in chain(ranges1, ranges2))
    max_ = max(input.stop for input, _ in chain(ranges1, ranges2))
    ranges1 = fill_ranges(ranges1, min_, max_) if fill_input else ranges1
    ranges2 = fill_ranges(ranges2, min_, max_)
    return chain.from_iterable(map(partial(compose_range, ranges2), ranges1))


def compose_maps(map1: Map, map2: Map, fill_input: bool = True) -> Map:
    assert map1.target == map2.source
    return Map(
        map1.source, map2.target, compose_ranges(map1.ranges, map2.ranges, fill_input=fill_input)
    )


def compose_all_maps(maps: Iterable[Map], start_type: Category) -> Map:
    source_to_map = {m.source: m for m in maps}

    def next_map(map: Map) -> Map:
        return source_to_map.get(map.target, Map("", "", []))

    ordered_maps = takewhile(bool, iterate(next_map, source_to_map[start_type]))
    return reduce(compose_maps, ordered_maps)


def parse_range(line: str) -> MapRange:
    target, source, size = map(int, line.split(maxsplit=2))
    return range(source, source + size), range(target, target + size)


def parse_map(block: str) -> Map:
    lines = block.splitlines(keepends=False)
    header = lines[0]
    cat1, _, cat2_ = header.split("-", maxsplit=2)
    cat2 = cat2_.split(maxsplit=1)[0]
    return Map(cat1, cat2, map(parse_range, lines[1:]))


def parse(input: Iterable[str]) -> Iterator[Map]:
    return parse_blocks(input, parse_map)


def parse_seeds(line: str) -> List[ID]:
    _, ids = line.split(":")
    return list(map(int, ids.strip().split()))


def parse_ranges(line: str) -> Iterable[IDRange]:
    seeds = parse_seeds(line)
    return (range(start, start + size) for start, size in chunked(2, seeds))


def run(input: IO[str], part_2: bool = True) -> int:
    lines = iter(input)
    seeds_line = next(lines)
    maps = parse_blocks(lines, parse_map)
    final_map = compose_all_maps(maps, "seed")
    if part_2:
        seed_ranges = list(parse_ranges(seeds_line))
        final_map = compose_maps(
            Map("seed", "seed", zip(seed_ranges, seed_ranges)), final_map, fill_input=False
        )
        seeds = final_map.starts
    else:
        seeds = parse_seeds(seeds_line)

    return min(map(final_map, seeds))


_TEST_INPUT = """
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 35
    assert run(f(_TEST_INPUT), part_2=True) == 46
