# Advent of Code 2022 daily solutions

In these solutions I strive for elegance, generality, and efficiency, simultaneously if possible.
Time-to-solution was not a metric I measured myself by, preferring aesthetics above all.
The ultimate goal is to solve each problem in a purely functional paradigm, with no loops or mutable local variables.
To this end, I've written a decorator, [`@tail_recursive`](solutions/tailrec.py#L35), which allows writing
tail-recursive functions in a purely functional style without incurring unbounded stack height and extra function calls.
This operates at the byte code level.
I experimented with an AST-based solution, but found operating at the byte code level more satisfactory.
This _does_ mean that much of the code in this repo is restricted to running in CPython (as opposed to e.g. PyPy).

## Initialize the environment

From repo root, run:

```shell
poetry install
```

## Run a solution

```shell
# help on the commands documented below
./main --help

# run solution to day 1 problem
./main run 1

# show info about the day 10 problem, including optional arguments that can be passed with --args <name>=<json_value>
./main info 10

# run tests for day 12 problem
./main test 12

# run day 24 solution with particular input read from stdin as opposed to the default input file
cat my_input.txt | ./main run 24
```
