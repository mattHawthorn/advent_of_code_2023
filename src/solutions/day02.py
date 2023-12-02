from functools import partial, reduce
from operator import mul
from typing import IO, DefaultDict, Iterable, Iterator, Literal, NamedTuple, Sequence, cast

Color = Literal["red", "green", "blue"]
Draw = DefaultDict[Color, int]


class Game(NamedTuple):
    id: int
    draws: Sequence[Draw]


def parse_draw(s: str) -> Draw:
    draws = (d.split(" ", maxsplit=1) for d in s.strip().split(", "))
    return Draw(int, {cast(Color, color): int(count) for count, color in draws})


def parse_line(line: str) -> Game:
    id_, draws = line.split(":", 1)
    return Game(int(id_.split(" ")[-1]), list(map(parse_draw, draws.split(";"))))


def parse(input: Iterable[str]) -> Iterator[Game]:
    return map(parse_line, map(str.strip, input))


def is_possible(counts: Draw, game: Game) -> bool:
    return all(all(count <= counts[color] for color, count in draw.items()) for draw in game.draws)


def max_(draw1: Draw, draw2: Draw) -> Draw:
    return Draw(int, {color: max(draw1[color], draw2[color]) for color in set(draw1).union(draw2)})


def power(game: Game) -> int:
    fewest_satisfiable = reduce(max_, game.draws)
    return reduce(mul, filter(bool, fewest_satisfiable.values()))


def run(input: IO[str], part_2: bool = True) -> int:
    games = parse(input)
    if part_2:
        powers = map(power, games)
        return sum(powers)
    else:
        counts = Draw(int, {"red": 12, "green": 13, "blue": 14})
        possible_games = filter(partial(is_possible, counts), games)
        return sum(game.id for game in possible_games)


def test():
    import io

    input_ = "Game 1: 1 red, 2 blue, 3 green; 2 green, 3 blue, 3 red\nGame 2: 15 red, 0 green"
    f = io.StringIO
    assert run(f(input_), part_2=False) == 1
    assert run(f(input_), part_2=True) == 3**3 + 15
