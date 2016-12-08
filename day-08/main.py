"""Advent of Code 2016 - Day 8."""

import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class Command:
    """Abstract command to be applied to a screen."""

    # Regular expression for parsing rect commands.
    RECT_REGEXP = re.compile(r'^rect (\d+)x(\d+)$')

    # Regular expression for parsing rotate commands.
    ROTATE_REGEXP = re.compile(r'^rotate (row y=|column x=)(\d+) by (\d+)$')

    @classmethod
    def from_line(cls, line):
        """Initialize a command from a line from the input file."""
        rect_match = cls.RECT_REGEXP.search(line)
        if rect_match:
            width, height = rect_match.groups()
            return RectCommand(int(width), int(height))

        rotate_match = cls.ROTATE_REGEXP.search(line)
        if rotate_match:
            direction, offset, shift = rotate_match.groups()
            return RotateCommand(direction[0], int(offset), int(shift))

        raise ValueError('Failed to parse line as a rect/rotate command.')


class RectCommand(Command):
    """Command that sets a rectangle of the screen to one."""

    def __init__(self, width, height):
        """Initialize a rect command from width and height."""
        self.width = width
        self.height = height

    def __str__(self):
        """Provide a human-readable representation of a rect command."""
        return 'rect {}x{}'.format(self.width, self.height)


class RotateCommand(Command):
    """Command that rotates a row or column of the screen by a given amount."""

    def __init__(self, direction, offset, shift):
        """Initialize a rotate command from direction, offset, and shift."""
        self.direction = direction
        self.offset = offset
        self.shift = shift

    def __str__(self):
        """Provide a human-readable representation of a rotate command."""
        prefix = {'r': 'row y', 'c': 'column x'}[self.direction]
        return 'rotate {}={} by {}'.format(prefix, self.offset, self.shift)


class Screen:
    """Monochrome screen in the Easter Bunny Headquarters."""

    # Bitmap font data used on screen with letters of size 5-by-6 pixels.
    FONT_DATA = [
        ('C', [0b00110, 0b01001, 0b00001, 0b00001, 0b01001, 0b00110]),
        ('H', [0b01001, 0b01001, 0b01111, 0b01001, 0b01001, 0b01001]),
        ('J', [0b01100, 0b01000, 0b01000, 0b01000, 0b01001, 0b00110]),
        ('K', [0b01001, 0b00101, 0b00011, 0b00101, 0b00101, 0b01001]),
        ('L', [0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b01111]),
        ('P', [0b00111, 0b01001, 0b01001, 0b00111, 0b00001, 0b00001]),
        ('R', [0b00111, 0b01001, 0b01001, 0b00111, 0b00101, 0b01001]),
        ('Y', [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100]),
        ('Z', [0b01111, 0b01000, 0b00100, 0b00010, 0b00001, 0b01111]),
    ]

    @classmethod
    def from_text(cls, text):
        """Initialize a screen from a string of text."""
        length = len(text)
        screen = cls(length * 5, 6)
        alphabet = dict(cls.FONT_DATA)
        for index, letter in enumerate(text):
            bitmap = alphabet.get(letter)
            if bitmap is None:
                raise ValueError('Letter {} not available.'.format(letter))
            shift = index * 5
            for row_index, row in enumerate(bitmap):
                screen.rows[row_index] |= (row << shift) & screen.row_mask
        return screen

    def __init__(self, width, height):
        """Initialize an empty screen."""
        self.width = width
        self.height = height
        self.rows = [0] * height
        self.row_mask = (1 << width) - 1

    def apply(self, command):
        """Apply a command or a list of commands to screen."""
        if isinstance(command, Command):
            self.__apply_command(command)
        else:
            self.__apply_iterable(command)

    def lit_pixels(self):
        """Count the number of lit pixels on screen."""
        lit = 0
        for row in self.rows:
            while row > 0:
                if row & 1:
                    lit += 1
                row >>= 1
        return lit

    def to_text(self):
        """Return a string by performing OCR on the screen contents."""
        if (self.width % 5 != 0) or (self.height != 6):
            raise ValueError('Display has an unexpected size.')
        letter_mask = (1 << 5) - 1
        length = self.width // 5
        text = []
        for index in range(length):
            shift = index * 5
            bitmap = [(row >> shift) & letter_mask for row in self.rows]
            for letter, letter_bitmap in self.FONT_DATA:
                if letter_bitmap == bitmap:
                    text.append(letter)
                    break
            else:
                raise ValueError('Failed to recognize letter {}'.format(index))
        return ''.join(text)

    def __str__(self):
        """Provide a human-readable representation of a screen."""
        return '\n'.join(map(self.__format_row, self.rows))

    def __apply_command(self, command):
        """FIXME."""
        if isinstance(command, RectCommand):
            self.__apply_rect(command)
        elif isinstance(command, RotateCommand):
            if command.direction == 'c':
                self.__apply_rotate_column(command)
            elif command.direction == 'r':
                self.__apply_rotate_row(command)
        else:
            raise ValueError('Encountered unrecognized command class.')

    def __apply_iterable(self, iterable):
        """Apply multiple commands from an iterable (usually a list)."""
        for command in iterable:
            self.__apply_command(command)

    def __apply_rect(self, command):
        """Apply a rect command to screen."""
        column_bits = (1 << command.width) - 1
        for row_index in range(command.height):
            self.rows[row_index] |= column_bits

    def __apply_rotate_column(self, command):
        """Apply a column rotate command to screen."""
        column_mask = 1 << command.offset
        column_data = [row & column_mask for row in self.rows]
        for row_index, row in enumerate(self.rows):
            shifted = (row_index + self.height - command.shift) % self.height
            self.rows[row_index] = (row & ~column_mask) | column_data[shifted]

    def __apply_rotate_row(self, command):
        """Apply a row rotate command to screen."""
        row_data = self.rows[command.offset]
        shifted = row_data << command.shift
        wrapped = row_data >> (self.width - command.shift)
        self.rows[command.offset] = (shifted & self.row_mask) | wrapped

    def __format_row(self, row):
        """Format a single row for pretty printing."""
        padded_bin = ''.join(reversed(bin(row)[2:].rjust(self.width, '0')))
        return padded_bin.replace('0', '.').replace('1', '#')


def main():
    """Main entry point of puzzle solution."""
    screen = Screen(50, 6)
    commands = [Command.from_line(line) for line in read_input()]
    screen.apply(commands)

    part_one = screen.lit_pixels()
    part_two = screen.to_text()

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
