"""Advent of Code 2016 - Day 3."""

import itertools
import os


def read_input():
    """Read input file and return as a list of integer triples."""
    base = os.path.abspath(os.path.dirname(__file__))
    file = os.path.join(base, 'input.txt')
    with open(file) as f:
        lines = f.read().splitlines()
        return [[int(number) for number in line.split()] for line in lines]


def sliced(iterable, n, fillvalue=None):
    """Yield fixed-length slices of the input."""
    return itertools.zip_longest(*[iter(iterable)] * n, fillvalue=fillvalue)


def transposed(matrix):
    """Transpose a matrix (list of nested lists of equal length)."""
    return [list(column) for column in zip(*matrix)]


def columnate(triples):
    """Yield columns of length 3 from a n-by-3 matrix in row-major form."""
    for matrix in sliced(triples, 3):
        yield from transposed(matrix)


def valid_triangle(triple):
    """Check whether a triple of side lengths represents a valid triangle."""
    return sum(triple) > 2 * max(triple)


def main():
    """Main entry point of puzzle solution."""
    triples = read_input()

    part_one = sum(map(valid_triangle, triples))
    part_two = sum(map(valid_triangle, columnate(triples)))

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
