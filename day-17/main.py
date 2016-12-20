"""Advent of Code 2016 - Day 17."""

import hashlib


def next_step(passcode, path, x, y):
    """Yield possible next steps for the current path and position."""
    digest = hashlib.md5(passcode + path).hexdigest()
    if digest[0] >= 'b' and y > 0:
        yield b'U', 0, -1
    if digest[1] >= 'b' and y < 3:
        yield b'D', 0, +1
    if digest[2] >= 'b' and x > 0:
        yield b'L', -1, 0
    if digest[3] >= 'b' and x < 3:
        yield b'R', +1, 0


def walk_paths(passcode):
    """Yield waves of all possible paths doing a breadth-first search."""
    old_wave = [(b'', 0, 0)]
    new_wave = []
    yield old_wave, []

    while True:
        for path, x, y in old_wave:
            for suffix, x_delta, y_delta in next_step(passcode, path, x, y):
                new_wave.append((path + suffix, x + x_delta, y + y_delta))

        solutions = [(index, path)
                     for index, (path, x, y) in enumerate(new_wave)
                     if (x == 3) and (y == 3)]

        if solutions:
            # Remove solutions from new wave because we cannot pass through the
            # room that contains the vault and return to it later.
            for index, _path in reversed(solutions):
                del new_wave[index]

        # Keep exploring the solution space until we absolutely cannot move.
        if not new_wave:
            break

        yield new_wave, [path for index, path in solutions]

        # Prepare for next wave.
        old_wave = new_wave
        new_wave = []


def shortest_path(passcode):
    """Find shortest path that leads to the vault."""
    for _wave, solutions in walk_paths(passcode):
        if solutions:
            if len(solutions) != 1:
                raise ValueError('Shortest path is not unique.')
            return solutions[0].decode('ascii')

    raise ValueError('Exhausted search space without finding a solution.')


def longest_path(passcode):
    """Find longest path that leads to the vault without passing it earlier."""
    longest_path = None
    for _wave, solutions in walk_paths(passcode):
        if solutions:
            longest_path = solutions[0].decode('ascii')

    if longest_path is None:
        raise ValueError('Exhausted search space without finding a solution.')

    return longest_path


def main():
    """Main entry point of puzzle solution."""
    INPUT_PASSCODE = b'pvhmgsws'

    part_one = shortest_path(INPUT_PASSCODE)
    part_two = len(longest_path(INPUT_PASSCODE))

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
