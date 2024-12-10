from collections import deque
from itertools import accumulate, chain
from typing import IO, Iterable, NamedTuple

import util


class BlockRange(NamedTuple):
    start: int
    width: int
    empty: bool
    id: int = -1

    @property
    def checksum(self) -> int:
        return (
            0
            if self.empty
            else self.id * (self.start * self.width + self.width * (self.width - 1) // 2)
        )


def compactify(
    data_blocks: list[BlockRange], empty_blocks: list[BlockRange], fragmented: bool
) -> list[BlockRange]:
    compactified = []
    data_blocks = list(data_blocks)
    empty_blocks = deque(empty_blocks)
    while data_blocks and empty_blocks:
        block = data_blocks.pop()
        while empty_blocks and empty_blocks[-1].start > block.start:
            empty_blocks.pop()
        remainder = block.width
        empties = []
        while (remainder > 0) and empty_blocks:
            empty = empty_blocks.popleft()
            remainder = (remainder - empty.width) if fragmented else (empty.width - block.width)
            if remainder >= 0:
                compactified.append(
                    BlockRange(
                        empty.start, empty.width if fragmented else block.width, False, block.id
                    )
                )
                if fragmented:
                    if remainder == 0:
                        break
                else:
                    if remainder > 0:
                        empties.append(
                            BlockRange(empty.start + block.width, remainder, True, empty.id)
                        )
                    break
            else:
                if fragmented:
                    extra = empty.width + remainder
                    compactified.append(BlockRange(empty.start, extra, False, block.id))
                    empties.append(
                        BlockRange(empty.start + extra, empty.width - extra, True, empty.id)
                    )
                    break
                else:
                    remainder = block.width
                    empties.append(empty)
        else:
            if fragmented:
                # never broke the while loop and no more empty blocks; extra data block at the end
                if remainder > 0:
                    compactified.append(BlockRange(block.start, remainder, False, block.id))
            else:
                # no empty space found
                compactified.append(block)

        empty_blocks.extendleft(reversed(empties))

    compactified.extend(data_blocks)
    return compactified


def checksum(blocks: Iterable[BlockRange]) -> int:
    return sum(map(BlockRange.checksum.fget, blocks))


def parse(input: Iterable[str]) -> tuple[list[BlockRange], list[BlockRange]]:
    widths = map(int, chain.from_iterable(map(str.strip, input)))

    def next_block(block: BlockRange, width: int) -> BlockRange:
        return BlockRange(
            block.start + block.width, width, not block.empty, block.id + (not block.empty)
        )

    all_blocks = accumulate(widths, next_block, initial=BlockRange(0, next(widths), False, 0))
    by_status = util.groupby(
        lambda block: block.empty, filter(lambda block: block.width > 0, all_blocks)
    )
    return by_status.get(False, []), by_status.get(True, [])


def run(input: IO[str], part_2: bool = True) -> int:
    data_blocks, empty_blocks = parse(input)
    compactified = compactify(data_blocks, empty_blocks, fragmented=not part_2)
    return checksum(compactified)


_test_input = """2333133121414131402"""


def test():
    import io

    f = io.StringIO
    util.assert_equal(run(f(_test_input), part_2=False), 1928)
    util.assert_equal(run(f(_test_input), part_2=True), 2858)
