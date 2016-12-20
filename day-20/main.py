"""Advent of Code 2016 - Day 20."""

from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


def ranges_overlap(range1, range2):
    """Check if two ranges overlap or are adjacent."""
    l1, u1 = range1
    l2, u2 = range2
    if (l1 <= l2 <= u1 <= u2) or (l2 <= l1 <= u2 <= u1):
        return True  # Partial overlap.
    elif (l1 <= l2 <= u2 <= u1) or (l2 <= l1 <= u1 <= u2):
        return True  # Complete overlap.
    elif (u1 + 1 == l2) or (u2 + 1 == l1):
        return True  # Adjacency.
    else:
        return False  # Disjoint.


def merge_ranges(range1, range2):
    """Merge two ranges that are known to overlap."""
    return min(range1[0], range2[0]), max(range1[1], range2[1])


def simplify_ranges(iranges):
    """Merge overlapping or adjacent ranges."""
    iranges = sorted(iranges)
    oranges = []

    # For every input range: Either merge it with an existing output range (if
    # they overlap) or add it to the list of output ranges (if no overlap).
    for irange in iranges:
        for index, orange in enumerate(oranges):
            if ranges_overlap(irange, orange):
                oranges[index] = merge_ranges(irange, orange)
                break
        else:
            oranges.append(irange)

    # Sorting the input ranges should make another simplification run obsolete,
    # but let's do it nonetheless, as we haven't thoroughly checked whether
    # this holds true in all possible cases. (It works with the puzzle input.)
    if len(iranges) != len(oranges):
        oranges = simplify_ranges(oranges)

    return oranges


def read_and_prepare_blacklist():
    """Read input file, convert to blacklisted ranges, and simplify them."""
    return simplify_ranges(tuple(map(int, line.split('-', 2)))
                           for line in read_input())


def lowest_accessible_ip(blacklist):
    """Determine the lowest IP address that is not on the blacklist."""
    lower, upper = blacklist[0]
    if lower == 0:
        return upper + 1
    else:
        return 0


def count_accessible_ips(blacklist):
    """Determine the number of addresses not on the blacklist."""
    blacklisted = 0
    for lower, upper in blacklist:
        blacklisted += upper - lower + 1
    return 2 ** 32 - blacklisted


def main():
    """Main entry point of puzzle solution."""
    blacklist = read_and_prepare_blacklist()

    part_one = lowest_accessible_ip(blacklist)
    part_two = count_accessible_ips(blacklist)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
