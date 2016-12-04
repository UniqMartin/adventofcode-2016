"""Advent of Code 2016 - Day 1."""

import collections
from pathlib import Path


def read_input():
    """Read input file and return comma-delimited items as a list."""
    text = Path(__file__).with_name('input.txt').read_text()
    return text.split(', ')


def walk_grid(instructions):
    """Yield positions on a grid while walking according to the instruction."""
    turn_map = {
        'L': dict(zip('NESW', 'WNES')),
        'R': dict(zip('NESW', 'ESWN')),
    }
    step_map = {
        'N': (0, +1),
        'E': (+1, 0),
        'S': (0, -1),
        'W': (-1, 0),
    }

    rotation = 'N'
    position = (0, 0)
    yield position

    for instruction in instructions:
        turn = instruction[0:1]
        step = int(instruction[1:])
        rotation = turn_map[turn][rotation]
        factor_x, factor_y = step_map[rotation]
        for _ in range(step):
            position = (position[0] + factor_x, position[1] + factor_y)
            yield position


def final_position(instructions):
    """Final position after following all instructions."""
    return collections.deque(walk_grid(instructions), maxlen=1).pop()


def first_intersection(instructions):
    """First position that is reached twice while following instructions."""
    trail = set()
    for position in walk_grid(instructions):
        if position in trail:
            return position
        else:
            trail.add(position)

    raise RuntimeError('Failed to find an intersection.')


def taxicab_norm(position):
    """Compute the taxicab norm of the given position."""
    return sum(map(abs, position))


def main():
    """Main entry point of puzzle solution."""
    instructions = read_input()

    part_one = taxicab_norm(final_position(instructions))
    part_two = taxicab_norm(first_intersection(instructions))

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
