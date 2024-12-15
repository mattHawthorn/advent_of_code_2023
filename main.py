#! /usr/bin/env python
import argparse
import json
import sys
import traceback
from importlib import import_module
from inspect import signature
from pathlib import Path
from time import perf_counter_ns
from typing import IO, Dict, List, Mapping, Optional, Protocol, Sequence, TypeVar, Union, cast

import util

INPUT_DIR = Path("inputs/")

Solution = TypeVar("Solution", covariant=True)
Param = Union[int, float, bool, str]


class Problem(Protocol[Solution]):
    def run(self, input_: IO[str], part_2: bool, **args: Param) -> Solution:
        ...

    def test(self):
        ...


class Options(Dict[str, Param]):
    pass


class Part(int):
    def __new__(cls, val: Union[int, str]):
        val_ = int(val)
        assert val_ in (1, 2), f"part must be 1 or 2: got {val}"
        return super().__new__(cls, val_)


def parse_param(args: List[str]):
    return {key: json.loads(val) for key, val in (a.split("=", maxsplit=1) for a in args)}


def parse_parts(args: List[str]) -> List[Part]:
    return list(map(Part, args))


def print_solution(solutions: list):
    for solution in solutions:
        print(solution)


def problem_name(problem: int) -> str:
    assert 1 <= problem <= 25, "problem number must be between 1 and 25, inclusive"
    return f"day{str(problem).zfill(2)}"


def import_problem(problem: int) -> Problem:
    name = problem_name(problem)
    return cast(Problem, import_module(f"solutions.{name}"))


def get_input(day: int) -> IO[str]:
    name = problem_name(day)
    filename = INPUT_DIR / (name + ".txt")
    return open(filename) if sys.stdin.isatty() else sys.stdin


parser = argparse.ArgumentParser(
    description="Run and test Matt Hawthorn's solutions to the 2024 Advent of Code problems",
    add_help=True,
)
commmands = parser.add_subparsers(dest="subcommand", required=True)
run = commmands.add_parser(
    "run",
    help=(
        "Run the solution to a particular day's problem. The default input is in the inputs/ "
        "folder, but input will be read from stdin if input is piped there."
    ),
)
run.add_argument(
    "day",
    type=int,
    help="the day number of the problem to solve (1-25)",
)
run.add_argument(
    "parts",
    nargs="*",
    type=parse_parts,  # type: ignore
    default=(Part(1), Part(2)),
    help="parts of the problem to solve (solve both parts 1 and 2 by default)",
)
run.add_argument(
    "--options",
    nargs="+",
    type=parse_param,  # type: ignore
    required=False,
    help=(
        "keyword arguments to pass to the problem solution in case it is parameterized. "
        "Run the `info` command for the problem in question to see its parameters."
    ),
)
run.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="print verbose output",
)
test = commmands.add_parser(
    "test",
    help="Run unit tests for functions used in the solution to a particular day's problem",
)
test.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="print verbose output",
)
test.add_argument(
    "day",
    type=int,
    help="the day number of the problem to run tests for (1-25)",
)
info = commmands.add_parser(
    "info",
    help=(
        "Print the doc string for a particular day's solution, providing some details about "
        "methodology"
    ),
)
info.add_argument(
    "day",
    type=int,
    help="the day number of the problem to print info for (1-25)",
)
input_ = commmands.add_parser(
    "input",
    help="Print the input text for a particular day's problem to stdout",
)
input_.add_argument(
    "day",
    type=int,
    help="the day number of the problem to print the input for (1-25)",
)


class AOC2023:
    """Run and test Matt Hawthorn's solutions to the 2024 Advent of Code problems"""

    def run(
        self,
        day: int,
        parts: Sequence[Part] = (Part(1), Part(2)),
        *,
        options: Optional[Options] = None,
        verbose: bool = False,
    ):
        util.set_verbose(verbose)
        problem = import_problem(day)
        kwargs: Mapping[str, Param] = options or {}
        return [self._run(day, problem, part, kwargs) for part in sorted(set(parts))]

    def _run(self, day: int, problem: Problem, part: Part, kwargs: Mapping[str, Param]):
        input_ = get_input(day)
        print(f"Running solution to part {part} of day {day}...", file=sys.stderr)
        tic = perf_counter_ns()
        solution = problem.run(input_, part == 2, **kwargs)
        toc = perf_counter_ns()
        print(f"Ran in {(toc - tic) / 1000000} ms", file=sys.stderr)
        return solution

    def test(self, day: int, verbose: bool):
        util.set_verbose(verbose)
        problem = import_problem(day)
        try:
            problem.test()
        except Exception as e:
            traceback.print_tb(e.__traceback__, file=sys.stderr)
        else:
            if not util._EXCEPTIONS:
                print(f"Tests pass for day {day}!")

    def info(self, day: int):
        problem = import_problem(day)
        print(f"Day {day} problem info:")
        if problem.__doc__:
            print(problem.__doc__, end="\n\n")
        print("Signature:")
        print(signature(problem.run))

    def input(self, day: int):
        for line in get_input(day):
            print(line, file=sys.stdout, end="")


if __name__ == "__main__":
    args = parser.parse_args()
    cmd = args.subcommand
    aoc = AOC2023()
    if cmd == "run":
        print_solution(aoc.run(args.day, args.parts, options=args.options, verbose=args.verbose))
    elif cmd == "test":
        aoc.test(args.day, verbose=args.verbose)
    elif cmd == "info":
        aoc.info(args.day)
    elif cmd == "input":
        aoc.input(args.day)
    else:
        raise ValueError(f"unknown subcommand: {cmd}")
