"""Advent of Code 2016 - Day 19."""

import itertools


def neighbor(elf_count):
    """Index of winning elf after taking turns stealing from left neighbor.

    This is a solution with an explicit formula that was developed from the
    observation that the winner is always an odd elf. The exact elf is
    determined by looking at the difference between the elf count and the
    highest power of two that is still less than or equal to the elf count,
    e.g. the winning elves for inputs 8..15 are 1, 3, 5, 7, 9, 11, 13, and 15.
    """
    offset = 2 ** (elf_count.bit_length() - 1)
    return 2 * (elf_count - offset) + 1


def neighbor_iterative(elf_count):
    """Index of winning elf after taking turns stealing from left neighbor.

    This is an iterative version of `neighbor` and was mainly used to verify
    the explicit formula used therein. It is infeasible for large elf counts.
    """
    # This is a list of an elf's immediate neighbor and is used like a linked
    # list. Inactive elves are those that are no longer reachable from others.
    active = [(elf_index + 1) % elf_count for elf_index in range(elf_count)]

    num_active = elf_count
    self_index = 0
    while num_active > 1:
        # Eliminate one elf.
        neighbor_index = active[self_index]
        active[self_index] = active[neighbor_index]
        num_active -= 1

        # Advance to next elf.
        self_index = active[self_index]

    return self_index + 1


def across(elf_count):
    """Index of winning elf after taking turns stealing from opposite elf.

    This is a solution with an almost explicit formula (aside from the somewhat
    clunky range search) that was developed from looking at patterns in the
    result of the iterative version. Determining the solution involves finding
    the right interval to look at and then dividing it in two, e.g. the winning
    elves for inputs 10..27 are 1..9 (lower half) and 11, 13, ..., 27 (upper).
    """
    # Handle the degenerate case first.
    if elf_count < 2:
        return 1

    # Determine the interval of size 2 * (3 ** n) that contains the elf count.
    lower_bound = 1
    upper_bound = 2
    for chunk_index in itertools.count():
        lower_bound = upper_bound
        upper_bound += 2 * (3 ** chunk_index)
        if lower_bound <= elf_count < upper_bound:
            break

    # Determine the winning elf from where the elf count is located in that
    # interval. Entries in the lower half start at one and increase by 1 while
    # entries in the upper half increase by 2. By the time the upper bounds is
    # reached, the upper bound and the winning elf coincide.
    middle_bound = (lower_bound + upper_bound) // 2
    if elf_count < middle_bound:
        offset = elf_count - lower_bound
        return offset + 1
    else:
        offset = upper_bound - elf_count
        return upper_bound - 2 * offset + 1


def across_iterative(elf_count):
    """Index of winning elf after taking turns stealing from opposite elf.

    This is an iterative version of `across` and was mainly used to verify the
    explicit formula used therein. It is infeasible for large elf counts.
    """
    active = [(elf_index + 1) % elf_count for elf_index in range(elf_count)]

    num_active = elf_count
    self_index = 0
    while num_active > 1:
        # Eliminate one elf.
        across_index = self_index
        across_offset = num_active // 2  # Steal from left one if two across.
        for _ in range(across_offset - 1):
            across_index = active[across_index]
        neighbor_index = active[across_index]
        active[across_index] = active[neighbor_index]
        num_active -= 1

        # Advance to next elf.
        self_index = active[self_index]

    return self_index + 1


def main():
    """Main entry point of puzzle solution."""
    INPUT_ELF_COUNT = 3005290

    part_one = neighbor(INPUT_ELF_COUNT)
    part_two = across(INPUT_ELF_COUNT)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
