from collections import Counter
from enum import IntEnum
from functools import partial
from itertools import count
from operator import mul
from typing import IO, Callable, Dict, Iterable, NamedTuple, Tuple, Type

JOKER = 1

Card = int


class HandKind(IntEnum):
    High = 0
    Pair = 1
    TwoPairs = 2
    ThreeOfAKind = 3
    FullHouse = 4
    FourOfAKind = 5
    FiveOfAKind = 6


SIGNATURE_TO_KIND: Dict[Tuple[int, ...], HandKind] = {
    (5,): HandKind.FiveOfAKind,
    (4, 1): HandKind.FourOfAKind,
    (3, 2): HandKind.FullHouse,
    (3, 1, 1): HandKind.ThreeOfAKind,
    (2, 2, 1): HandKind.TwoPairs,
    (2, 1, 1, 1): HandKind.Pair,
    (1, 1, 1, 1, 1): HandKind.High,
}


class Hand(Tuple[Card, Card, Card, Card, Card]):
    @property
    def signature(self) -> Tuple[int, ...]:
        return tuple(sorted(Counter(self).values(), reverse=True))

    @property
    def kind(self) -> HandKind:
        return SIGNATURE_TO_KIND[self.signature]

    def __lt__(self, other):
        self_kind, other_kind = self.kind, other.kind
        if self_kind < other_kind:
            return True
        elif self_kind > other_kind:
            return False
        else:
            return super().__lt__(other)

    def __gt__(self, other):
        return self != other and not self < other


class InterestingHand(Hand):
    @property
    def signature(self) -> Tuple[int, ...]:
        simple_signature = super().signature
        joker_count = self.count(JOKER)
        if joker_count in (0, 5):
            return simple_signature
        elif joker_count == 4:
            return (5,)
        elif joker_count == 3:
            return (4, 1) if min(simple_signature) == 1 else (5,)
        elif joker_count == 2:
            return (
                (5,)
                if max(simple_signature) == 3
                else ((4, 1) if len(simple_signature) == 3 else (3, 1, 1))
            )
        else:
            max_count = max(simple_signature)
            return (
                (5,)
                if max_count == 4
                else (
                    (4, 1)
                    if max_count == 3
                    else (
                        (3, 2)
                        if len(simple_signature) == 3
                        else ((3, 1, 1) if len(simple_signature) == 4 else (2, 1, 1, 1))
                    )
                )
            )


class Bid(NamedTuple):
    hand: Hand
    bid: int


def score(bids: Iterable[Bid]) -> int:
    ordered = sorted(bids, key=lambda bid: bid.hand)
    return sum(map(mul, (bid.bid for bid in ordered), count(1)))


def parse_standard_card(s: str) -> Card:
    return int(s) if s.isdigit() else 10 + "TJQKA".index(s)


def parse_joker_card(s: str) -> Card:
    return int(s) if s.isdigit() else JOKER if s == "J" else 10 + "TQKA".index(s)


def parse_bid(parse_card: Callable[[str], Card], hand_type: Type[Hand], line: str):
    hand_str, bid_str = line.split(maxsplit=1)
    assert len(hand_str) == 5
    return Bid(hand_type(map(parse_card, hand_str)), int(bid_str))


def run(input: IO[str], part_2: bool = True) -> int:
    hand_type: Type[Hand]

    if part_2:
        card_type, hand_type = parse_joker_card, InterestingHand
    else:
        card_type, hand_type = parse_standard_card, Hand

    bids = map(partial(parse_bid, card_type, hand_type), input)
    return score(bids)


_TEST_INPUT = """
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483""".strip()


def test():
    import io

    f = io.StringIO
    assert run(f(_TEST_INPUT), part_2=False) == 6440
    assert run(f(_TEST_INPUT), part_2=True) == 5905
