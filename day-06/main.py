"""Advent of Code 2016 - Day 6."""

import itertools
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


def transposed(matrix):
    """Transpose a matrix (list of nested lists of equal length)."""
    return [list(column) for column in zip(*matrix)]


def recover_message(columns, frequency):
    """Recover message from columns by finding most/least common letters."""
    if frequency == 'most':
        reverse = True
    elif frequency == 'least':
        reverse = False
    else:
        raise ValueError('Argument frequency has an invalid value.')

    message = []
    for column in columns:
        letter_stats = []
        for letter, group in itertools.groupby(sorted(column)):
            letter_stats.append((len(list(group)), letter))
        message.append(sorted(letter_stats, reverse=reverse)[0][1])

    return ''.join(message)


def main():
    """Main entry point of puzzle solution."""
    columns = transposed(read_input())

    part_one = recover_message(columns, frequency='most')
    part_two = recover_message(columns, frequency='least')

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
