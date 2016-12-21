"""Advent of Code 2016 - Day 21."""

import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


def swap_by_index(password, _inverse, index1, index2):
    """Swap two letters in two fixed positions."""
    index1, index2 = int(index1), int(index2)
    password[index1], password[index2] = password[index2], password[index1]
    return password


def swap_by_letter(password, _inverse, letter1, letter2):
    """Swap all occurrences of the two given letters in the string."""
    indices1 = [i for i, l in enumerate(password) if l == letter1]
    indices2 = [i for i, l in enumerate(password) if l == letter2]
    for i in indices1:
        password[i] = letter2
    for i in indices2:
        password[i] = letter1
    return password


def rotate_by_offset(password, inverse, direction, offset):
    """Rotate by a fixed offset in a given direction."""
    offset = int(offset) % len(password)
    if (direction == 'right') ^ inverse:
        offset = -offset
    return password[offset:] + password[:offset]


def rotate_by_letter(password, inverse, letter):
    """Rotate depending on the position of a letter in the string."""
    index = password.index(letter)
    if inverse:
        # This transformation cannot be inverted for arbitrary inputs, but it
        # works for inputs of length 8 (as used in the puzzle input).
        if len(password) != 8:
            raise ValueError('Can only unscramble passwords of length 8!')
        if index == 0:
            offset = -1
        elif index % 2 == 1:
            offset = -(1 + index) // 2
        else:
            offset = -5 - index // 2
    else:
        offset = (index + 1 + (index >= 4)) % len(password)
    return password[-offset:] + password[:-offset]


def reverse_range(password, _inverse, lower, upper):
    """Reverse a part of the string with both bounds being inclusive."""
    lower, upper = int(lower), int(upper) + 1
    password[lower:upper] = reversed(password[lower:upper])
    return password


def move_letter(password, inverse, from_index, to_index):
    """Move a letter from one position to another."""
    if inverse:
        from_index, to_index = to_index, from_index
    from_index, to_index = int(from_index), int(to_index)
    password.insert(to_index, password.pop(from_index))
    return password


def scramble_password(password, instructions, unscramble=False):
    """Scramble a password according to the given instructions."""
    patterns = [
        (r'^swap position (\d+) with position (\d+)$', swap_by_index),
        (r'^swap letter ([a-z]) with letter ([a-z])$', swap_by_letter),
        (r'^rotate (left|right) (\d+) steps?$', rotate_by_offset),
        (r'^rotate based on position of letter ([a-z])$', rotate_by_letter),
        (r'^reverse positions (\d+) through (\d+)$', reverse_range),
        (r'^move position (\d+) to position (\d+)$', move_letter),
    ]

    if unscramble:
        instructions = reversed(instructions)

    password = list(password)
    for instruction in instructions:
        for pattern, handler in patterns:
            match = re.search(pattern, instruction)
            if match is not None:
                password = handler(password[:], unscramble, *match.groups())
                break
        else:
            raise ValueError('Unrecognized instruction.')

    return ''.join(password)


def unscramble_password(password, instructions):
    """Unscramble a password according to the given instructions."""
    return scramble_password(password, instructions, unscramble=True)


def main():
    """Main entry point of puzzle solution."""
    INPUT_PASSWORD = 'abcdefgh'
    INPUT_SCRAMBLED = 'fbgdceah'

    instructions = read_input()

    part_one = scramble_password(INPUT_PASSWORD, instructions)
    part_two = unscramble_password(INPUT_SCRAMBLED, instructions)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
