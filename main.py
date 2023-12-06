#! /usr/bin/env python
import json
import sys
import warnings
from importlib import import_module
from inspect import signature
from pathlib import Path
from time import perf_counter_ns
from typing import IO, Dict, List, Mapping, Optional, Protocol, Sequence, TypeVar, Union, cast

from bourbaki.application.cli import CommandLineInterface, cli_spec  # type: ignore
from bourbaki.application.typed_io.cli_parse import cli_parser  # type: ignore
from bourbaki.application.typed_io.cli_repr_ import cli_repr  # type: ignore

warnings.filterwarnings("ignore", r".* jump offsets", category=UserWarning, module=r".*\.tailrec")

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


cli_repr.register(Options, as_const=True)("<name>=<value:json>")
cli_repr.register(Sequence[Part], as_const=True)("[1|2  ...]")


@cli_parser.register(Options, as_const=True, derive_nargs=True)
def parse_param(args: List[str]):
    return {key: json.loads(val) for key, val in (a.split("=", maxsplit=1) for a in args)}


@cli_parser.register(Sequence[Part], as_const=True, derive_nargs=True)
def parse_parts(args: List[str]) -> List[Part]:
    return list(map(Part, cli_parser(List[int])(args)))


def print_solution(solutions: List):
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


cli = CommandLineInterface(
    prog="main",
    require_options=False,
    require_subcommand=True,
    implicit_flags=True,
    use_verbose_flag=True,
)


@cli.definition
class AOC2023:
    """Run and test Matt Hawthorn's solutions to the 2023 Advent of Code problems"""

    @cli_spec.output_handler(print_solution)
    def run(
        self,
        day: int,
        parts: Sequence[Part] = (Part(1), Part(2)),
        *,
        options: Optional[Options] = None,
    ):
        """Run the solution to a particular day's problem. The default input is in the inputs/
        folder, but input will be read from stdin if input is piped there.

        :param day: the day number of the problem to solve (1-25)
        :param parts: parts of the problem to solve (solve both parts 1 and 2 by default)
        :param options: keyword arguments to pass to the problem solution in case it is
          parameterized. Run the `info` command for the problem in question to see its parameters.
        """
        problem = import_problem(day)
        kwargs: Mapping[str, Param] = options or {}
        return [self._run(day, problem, part, kwargs) for part in sorted(parts)]

    def _run(self, day: int, problem: Problem, part: Part, kwargs: Mapping[str, Param]):
        input_ = get_input(day)
        print(f"Running solution to part {part} of day {day}...", file=sys.stderr)
        tic = perf_counter_ns()
        solution = problem.run(input_, part == 2, **kwargs)
        toc = perf_counter_ns()
        print(f"Ran in {(toc - tic) / 1000000} ms", file=sys.stderr)
        return solution

    def test(self, day: int):
        """Run unit tests for functions used in the solution to a particular day's problem

        :param day: the day number of the problem to run tests for (1-25)
        """
        problem = import_problem(day)
        problem.test()
        print(f"Tests pass for day {day}!")

    def info(self, day: int):
        """Print the doc string for a particular day's solution, providing some details about
        methodology.

        :param day: the day number of the problem to run tests for (1-25)
        """
        problem = import_problem(day)
        print(f"Day {day} problem info:")
        if problem.__doc__:
            print(problem.__doc__, end="\n\n")
        print("Signature:")
        print(signature(problem.run))

    def input(self, day: int):
        """Print the input text for a particular day's problem to stdout"""
        with open(f"inputs/day{str(day).zfill(2)}.txt", "r") as f:
            for line in f:
                print(line, file=sys.stdout, end="")


if __name__ == "__main__":
    cli.run()
