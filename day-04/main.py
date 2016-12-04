"""Advent of Code 2016 - Day 4."""

import itertools
import operator
import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class Room:
    """Room in the Easter Bunny HQ (either real or decoy)."""

    # Regular expression for parsing encrypted/checksummed room names.
    ROOM_REGEXP = re.compile(r'^(?P<name>[a-z-]+)-(?P<sector_id>\d+)'
                             r'\[(?P<checksum>[a-z]+)\]$')

    @classmethod
    def from_line(cls, line):
        """Initialize a room from a line from the input file."""
        match = cls.ROOM_REGEXP.search(line)
        return cls(match.group('name'),
                   int(match.group('sector_id')),
                   match.group('checksum'))

    def __init__(self, name, sector_id, checksum):
        """Initialize a room from its name, sector ID, and checksum."""
        self.__is_real = None
        self.__mapping = None
        self.name = name
        self.sector_id = sector_id
        self.checksum = checksum

    def is_real(self):
        """Whether the room is real."""
        if self.__is_real is None:
            self.__is_real = self.__compute_checksum() == self.checksum
        return self.__is_real

    def is_storage(self):
        """Whether the room is the sought North Pole object storage room."""
        return (self.is_real() and
                self.decrypted_name() == 'northpole object storage')

    def decrypted_name(self):
        """Decrypted room name."""
        if self.__mapping is None:
            self.__mapping = self.__setup_mapping()
        return ''.join(self.__mapping[letter] for letter in self.name)

    def __setup_mapping(self):
        """Setup letter mapping needed for decrypting the room name."""
        ord_a = ord('a')
        shift = self.sector_id
        source = [chr(ord_a + letter) for letter in range(26)]
        target = [chr(ord_a + (letter + shift) % 26) for letter in range(26)]
        mapping = dict(zip(source, target))
        mapping['-'] = ' '
        return mapping

    def __compute_checksum(self):
        """Compute the actual checksum from the (encrypted) room name."""
        clean_name = self.name.replace('-', '')
        statistics = []
        for letter, group in itertools.groupby(sorted(clean_name)):
            statistics.append((len(list(group)), letter))
        frequency_getter = operator.itemgetter(0)
        statistics = sorted(statistics, key=frequency_getter, reverse=True)
        checksum = ''.join(letter for frequency, letter in statistics[:5])
        return checksum


def storage_room(rooms):
    """Find the sought North Pole object storage room."""
    storage_rooms = [room for room in rooms if room.is_storage()]
    if len(storage_rooms) == 1:
        return storage_rooms[0]
    raise RuntimeError('Failed to uniquely identify the storage room.')


def main():
    """Main entry point of puzzle solution."""
    rooms = [Room.from_line(line) for line in read_input()]

    part_one = sum(room.sector_id for room in rooms if room.is_real())
    part_two = storage_room(rooms).sector_id

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
