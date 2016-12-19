"""Advent of Code 2016 - Day 16."""


def expand_pattern(pattern, length):
    """Expand the given pattern using a modified dragon curve."""
    while len(pattern) < length:
        flipped = bytes(byte ^ 1 for byte in reversed(pattern))
        pattern = pattern + b'0' + flipped

    return pattern[:length]


def checksum_pattern(pattern):
    """Compute the checksum of a given pattern."""
    if len(pattern) == 0:
        return pattern

    while len(pattern) % 2 == 0:
        lhs = pattern[0::2]
        rhs = pattern[1::2]
        pattern = bytes((a & ~1) | (1 ^ a ^ b) for a, b in zip(lhs, rhs))

    return pattern


def checksum_disk(pattern, length):
    """Expand pattern to length of disk and then compute its checksum."""
    return checksum_pattern(expand_pattern(pattern, length)).decode('ascii')


def main():
    """Main entry point of puzzle solution."""
    INPUT_PATTERN = b'11011110011011101'

    print('Part One: {}'.format(checksum_disk(INPUT_PATTERN, 272)))
    print('Part Two: {}'.format(checksum_disk(INPUT_PATTERN, 35651584)))


if __name__ == '__main__':
    main()
