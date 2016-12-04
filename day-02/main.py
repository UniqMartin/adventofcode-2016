"""Advent of Code 2016 - Day 2."""

from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class Keypad:
    """Keypad with configurable layout and transitions between buttons."""

    # Mapping of movement commands to Cartesian coordinate offsets.
    MOVE_MAP = {
        'U': (-1, 0),
        'D': (+1, 0),
        'L': (0, -1),
        'R': (0, +1),
    }

    @classmethod
    def create_square(cls):
        """Initialize a keypad with a traditional square layout."""
        return cls(['123',
                    '456',
                    '789'])

    @classmethod
    def create_diamond(cls):
        """Initialize a keypad with a fancy diamond layout."""
        return cls(['  1  ',
                    ' 234 ',
                    '56789',
                    ' ABC ',
                    '  D  '])

    def __init__(self, layout):
        """Initialize a keypad with a layout and compute its transitions."""
        self.transitions = {}

        # Scan the entire keypad layout (assuming a rectangular shape).
        rows = len(layout)
        cols = len(layout[0])
        for row_index, row in enumerate(layout):
            for col_index, button in enumerate(row):
                if button == ' ':
                    continue

                # Construct all possible transitions from current button.
                for move, (row_offset, col_offset) in self.MOVE_MAP.items():
                    # Determine new position and skip if outside of keypad.
                    next_row = row_index + row_offset
                    if (next_row < 0) or (next_row >= rows):
                        continue
                    next_col = col_index + col_offset
                    if (next_col < 0) or (next_col >= cols):
                        continue

                    # Determine new button, but skip empty space.
                    next_button = layout[next_row][next_col]
                    if next_button == ' ':
                        continue

                    # Save valid transition (button and direction).
                    self.transitions[(button, move)] = next_button

    def get_code(self, instructions):
        """Determine the code that would result from the given instructions."""
        button = '5'
        code = []
        for line in instructions:
            button = self.__get_digit(line, button)
            code.append(button)
        return ''.join(code)

    def __get_digit(self, moves, button):
        """Determine one digit of the code from a single instruction line."""
        for move in moves:
            next_button = self.transitions.get((button, move))
            if next_button:
                button = next_button
        return button


def main():
    """Main entry point of puzzle solution."""
    instructions = read_input()

    part_one = Keypad.create_square().get_code(instructions)
    part_two = Keypad.create_diamond().get_code(instructions)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
