"""Advent of Code 2016 - Day 15."""

import functools
import operator
import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class Disc:
    """Disc with index, period length, and initial position."""

    # Regular expression for parsing a disc description.
    DISC_REGEXP = re.compile(r'Disc #(\d+) has (\d+) positions; at time=0, it '
                             r'is at position (\d+).')

    @classmethod
    def from_line(cls, line):
        """Initialize a disc from a line from the input file."""
        match = cls.DISC_REGEXP.search(line)
        return cls(int(match.group(1)),
                   int(match.group(2)),
                   int(match.group(3)))

    def __init__(self, index, period_length, initial_position):
        """Initialize a disc from its properties."""
        self.index = index
        self.period_length = period_length
        self.initial_position = initial_position


def egcd(b, n):
    """Compute the result of the extended Euclidean algorithm."""
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    while n != 0:
        q, b, n = b // n, n, b % n
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return b, x0, y0


def solve_congruences(coefficients, moduli):
    """Solve a system of linear congruences.

    Compute canonical solution x for linear system of congruences:
      x = coefficients[0] (mod moduli[0])
      x = coefficients[1] (mod moduli[1])
      ...
    """
    common_multiple = functools.reduce(operator.mul, moduli)
    solution = 0
    for coefficient, modulus in zip(coefficients, moduli):
        other = common_multiple // modulus
        gcd, _, y0 = egcd(modulus, other)
        if gcd != 1:
            raise ValueError('Detected moduli that are not coprime.')
        solution += coefficient * y0 * other

    return solution % common_multiple


def time_of_first_alignment(discs):
    """Compute first time where zero slot of all discs is aligned.

    The time t when all discs are aligned such that the capsule will be able to
    pass the slot (aligned with position 0) on every disc, can be computed by
    solving the following set of equations:
      t + disc_index[0] = ... * period_length[0] - initial_position[0]
      t + disc_index[1] = ... * period_length[1] - initial_position[1]
      ...

    Equivalently, this can be rephrased as a system of linear congruences:
      t = -disc_index[0] - initial_position[0] (mod period_length[0])
      t = -disc_index[1] - initial_position[1] (mod period_length[1])
      ...
    """
    moduli = [disc.period_length for disc in discs]
    coefficients = [-disc.index - disc.initial_position for disc in discs]

    return solve_congruences(coefficients, moduli)


def main():
    """Main entry point of puzzle solution."""
    discs = [Disc.from_line(line) for line in read_input()]
    extra_disc = Disc(len(discs) + 1, 11, 0)

    part_one = time_of_first_alignment(discs)
    part_two = time_of_first_alignment(discs + [extra_disc])

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
