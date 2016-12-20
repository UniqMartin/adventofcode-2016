"""Advent of Code 2016 - Day 18."""

from pathlib import Path


def read_input():
    """Read input file and return as string."""
    return Path(__file__).with_name('input.txt').read_text().rstrip()


class TileMap:
    """Tile map with rows that represent safe/trap tiles in a room."""

    # Set of predecessor triples that should result in a trap on the next row.
    TRAP_SET = {'..^', '.^^', '^..', '^^.'}

    def __init__(self, first_row):
        """Initialize a tile map from a given first row."""
        self.rows = [first_row]

    def advance_to(self, num_rows):
        """Advance the tile map to the given number of rows."""
        add_rows = num_rows - len(self.rows)
        for _ in range(add_rows):
            old = '.' + self.rows[-1] + '.'
            new = []
            for left, center, right in zip(old[:-2], old[1:-1], old[2:]):
                if left + center + right in self.TRAP_SET:
                    new.append('^')
                else:
                    new.append('.')
            self.rows.append(''.join(new))

        # Simplify chaining calls.
        return self

    def count(self, what):
        """Count the number of."""
        return sum(row.count(what) for row in self.rows)

    def print(self):
        """Print the entire tile map (mostly for debugging purposes)."""
        for row in self.rows:
            print(row)


def main():
    """Main entry point of puzzle solution."""
    tile_map = TileMap(read_input())

    print('Part One: {}'.format(tile_map.advance_to(40).count('.')))
    print('Part Two: {}'.format(tile_map.advance_to(400000).count('.')))


if __name__ == '__main__':
    main()
