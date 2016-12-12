"""Advent of Code 2016 - Day 9."""

import re
from pathlib import Path


def read_input():
    """Read input file and return as string."""
    return Path(__file__).with_name('input.txt').read_text().rstrip()


def decompress(compressed):
    """Yield chunk-repeat pairs while decompressing the input."""
    marker_re = re.compile(r'\((\d+)x(\d+)\)')
    offset = 0
    while offset < len(compressed):
        # Match an optional fixed chunk followed by a repetition marker.
        match = marker_re.search(compressed, pos=offset)
        if match is None:
            # Trailing fixed chunk without repetition marker.
            yield compressed[offset:], 1
            break

        # Determine boundaries of fixed and repeated chunks.
        repeated_length, repeat_count = map(int, match.groups())
        fixed_end, repeated_begin = match.span()
        repeated_end = repeated_begin + repeated_length

        # Deal with fixed chunk (if present).
        if offset < fixed_end:
            yield compressed[offset:fixed_end], 1

        # Deal with repetition marker and repeated chunk.
        yield compressed[repeated_begin:repeated_end], repeat_count

        # Advance to next chunk.
        offset = repeated_end


def decompress_recursively(compressed, max_depth=None):
    """Yield chunk-repeat pairs while recursively decompressing the input."""
    limit_depth = max_depth is not None
    if limit_depth and max_depth <= 0:
        yield compressed, 1
        return

    child_depth = max_depth - 1 if limit_depth else None
    for chunk, repeat_count in decompress(compressed):
        if repeat_count == 1 and chunk == compressed:
            # Truncate recursion because we've become stationary.
            yield chunk, repeat_count
        elif limit_depth and max_depth <= 1:
            # Truncate recursion because we've hit the recursion limit.
            yield chunk, repeat_count
        else:
            # Expand further.
            for c, rc in decompress_recursively(chunk, max_depth=child_depth):
                yield c, rc * repeat_count


def decompressed_length(compressed, max_depth=None):
    """Compute length of a decompressed text without materializing it."""
    return sum(len(chunk) * repeat_count
               for chunk, repeat_count
               in decompress_recursively(compressed, max_depth=max_depth))


def main():
    """Main entry point of puzzle solution."""
    compressed = read_input()

    part_one = decompressed_length(compressed, max_depth=1)
    part_two = decompressed_length(compressed)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
