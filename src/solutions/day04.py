from functools import partial, reduce
from itertools import chain, repeat, starmap, takewhile
from operator import add
from typing import IO, Collection, Counter, Mapping, NamedTuple

from util import iterate


class Card(NamedTuple):
    id: int
    winning: Collection[int]
    drawn: Collection[int]


def num_won(card: Card) -> int:
    return sum(1 for n in card.drawn if n in card.winning)


def score(card: Card) -> int:
    num_won_ = num_won(card)
    return 2 ** (num_won_ - 1) if num_won_ else 0


def play(id_to_card: Mapping[int, Card], id_to_count: Mapping[int, int]) -> Counter[int]:
    def won_copies(id: int, count: int) -> Counter[int]:
        won_ids = range(id + 1, id + 1 + num_won(id_to_card[id]))
        return Counter(dict(zip(filter(id_to_card.__contains__, won_ids), repeat(count))))

    return reduce(add, starmap(won_copies, id_to_count.items()))


def parse_card(s: str) -> Card:
    id_, rest = s.split(":", maxsplit=1)
    winning, drawn = rest.split("|", maxsplit=1)
    return Card(
        int(id_.split()[-1]),
        list(map(int, winning.strip().split())),
        list(map(int, drawn.strip().split())),
    )


def run(input: IO[str], part_2: bool = True) -> int:
    cards = list(map(parse_card, input))
    if part_2:
        id_to_card = {card.id: card for card in cards}
        countss = takewhile(bool, iterate(partial(play, id_to_card), {i: 1 for i in id_to_card}))
        return sum(chain.from_iterable((counts.values() for counts in countss)))
    else:
        return sum(map(score, cards))


_TEST_INPUT = """
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 13
    assert run(f(_TEST_INPUT), part_2=True) == 30
