from collections import Counter
from functools import partial
from itertools import count
from operator import mul
from typing import IO, Callable, Iterable, NamedTuple, Tuple, Type

JOKER = 1

Card = int
Hand = Tuple[Card, Card, Card, Card, Card]
# signature of a hand as descending counts of unique card types; e.g. full house is (3, 2)
# these sort in the natural order lexicographically
HandKind = Tuple[int, ...]


class StandardHand(Hand):
    @property
    def kind(self) -> HandKind:
        return tuple(sorted(Counter(self).values(), reverse=True))

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


class JokerHand(StandardHand):
    @property
    def kind(self) -> Tuple[int, ...]:
        return merge_jokers(self.count(JOKER), super().kind)


class Bid(NamedTuple):
    hand: StandardHand
    bid: int


def merge_jokers(joker_count: int, hand_kind: HandKind) -> HandKind:
    if len(hand_kind) == 1 or joker_count == 0:
        return hand_kind
    else:
        joker_ix = hand_kind.index(joker_count)
        sub_hand = tuple(n for i, n in enumerate(hand_kind) if i != joker_ix)
        max_count = max(sub_hand)
        max_ix = sub_hand.index(max_count)
        return (joker_count + max_count, *(n for i, n in enumerate(sub_hand) if i != max_ix))


def score(bids: Iterable[Bid]) -> int:
    ordered = sorted(bids, key=lambda bid: bid.hand)
    return sum(map(mul, (bid.bid for bid in ordered), count(1)))


def parse_standard_card(s: str) -> Card:
    return int(s) if s.isdigit() else 10 + "TJQKA".index(s)


def parse_joker_card(s: str) -> Card:
    return int(s) if s.isdigit() else JOKER if s == "J" else 10 + "TQKA".index(s)


def parse_bid(parse_card: Callable[[str], Card], hand_type: Type[StandardHand], line: str):
    hand_str, bid_str = line.split(maxsplit=1)
    assert len(hand_str) == 5
    return Bid(hand_type(map(parse_card, hand_str)), int(bid_str))


def run(input: IO[str], part_2: bool = True) -> int:
    hand_type: Type[StandardHand]

    if part_2:
        card_type, hand_type = parse_joker_card, JokerHand
    else:
        card_type, hand_type = parse_standard_card, StandardHand

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
