"""Advent of Code 2016 - Day 10."""

import re
import functools
import operator
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class Peer:
    """Base class for things that can receive values (from bots)."""


class Bot(Peer):
    """Bot zooming around in a factory that processes values."""

    def __init__(self, index):
        """Initialize an unused bot that hasn't been configured yet."""
        self.index = index
        self.peers = None
        self.values = []
        self.done = False

    def activate(self):
        """Activate a fully configured bot that is ready."""
        if self.done:
            raise ValueError('Bot {}: Unexpected reuse.'.formay(self.index))

        if len(self.values) != 2:
            raise ValueError('Bot {}: Values missing.'.format(self.index))

        if self.peers is None:
            raise ValueError('Bot {}: Peers missing.'.format(self.index))

        lo, hi = sorted(self.values)
        self.peers[0].give_value(lo)
        self.peers[1].give_value(hi)
        self.done = True

    def give_value(self, value):
        """Hand a value to a bot for later processing."""
        if len(self.values) >= 2:
            raise ValueError('Bot {}: Too many values.'.format(self.index))

        self.values.append(value)

    def is_ready(self):
        """Check whether the bot is ready (already received two values)."""
        return not self.done and len(self.values) == 2

    def set_peers(self, lo_peer, hi_peer):
        """Configure a bot by connecting it to its peers."""
        if self.peers is not None:
            raise ValueError('Bot {}: Unexpected reassignment of its '
                             'peers.'.format(self.index))

        self.peers = (lo_peer, hi_peer)


class Output(Peer):
    """Output of a factory that can receive values from bots."""

    def __init__(self, index):
        """Initialize an empty output."""
        self.index = index
        self.value = None

    def give_value(self, value):
        """Hand a value to an output for storage."""
        if self.value is not None:
            raise ValueError('Output {}: Unexpected reassignment of its '
                             'value.'.format(self.index))

        self.value = value


class Factory:
    """Factory with bots (that interact with each other) and outputs."""

    # Regular expression for parsing bot activity.
    BOT_REGEXP = re.compile(r'^bot (?P<bot_index>\d+) gives low to '
                            r'(?P<lo_kind>bot|output) (?P<lo_index>\d+) and '
                            r'high to (?P<hi_kind>bot|output) '
                            r'(?P<hi_index>\d+)$')

    # Regular expression for parsing bot initialization with a value.
    VALUE_REGEXP = re.compile(r'^value (?P<value>\d+) goes to bot '
                              r'(?P<bot_index>\d+)$')

    @classmethod
    def from_lines(cls, lines):
        """Initialize a factory from lines from the input file."""
        factory = cls()
        for line in lines:
            match = cls.BOT_REGEXP.search(line)
            if match:
                factory.add_bot(int(match.group('bot_index')),
                                match.group('lo_kind'),
                                int(match.group('lo_index')),
                                match.group('hi_kind'),
                                int(match.group('hi_index')))
                continue

            match = cls.VALUE_REGEXP.search(line)
            if match:
                factory.add_value(int(match.group('bot_index')),
                                  int(match.group('value')))
                continue

            raise ValueError('Failed to parse line "{}".'.format(line))

        return factory

    def __init__(self):
        """Initialize an empty factory."""
        self.bots = {}
        self.outputs = {}

    def add_bot(self, bot_index, lo_kind, lo_index, hi_kind, hi_index):
        """Add a bot to the factory and configure its peers."""
        bot = self.get_bot(bot_index)
        lo_peer = self.get_peer(lo_kind, lo_index)
        hi_peer = self.get_peer(hi_kind, hi_index)
        bot.set_peers(lo_peer, hi_peer)

    def add_value(self, bot_index, value):
        """Hand an initial value to a bot."""
        bot = self.get_bot(bot_index)
        bot.give_value(value)

    def get_bot(self, index):
        """Fetch a bot by index or create if it doesn't exist yet."""
        if index not in self.bots:
            self.bots[index] = Bot(index)
        return self.bots[index]

    def get_output(self, index):
        """Fetch an output by index or create if it doesn't exist yet."""
        if index not in self.outputs:
            self.outputs[index] = Output(index)
        return self.outputs[index]

    def get_peer(self, kind, index):
        """Fetch a peer by index (either bot or output) or create as needed."""
        if kind == 'bot':
            return self.get_bot(index)
        elif kind == 'output':
            return self.get_output(index)
        else:
            raise ValueError('Unexpected kind of peer "{}".'.format(kind))

    def simulate(self):
        """Simulate the bot activity by activating bots until all are done."""
        while True:
            for bot in self.bots.values():
                if bot.is_ready():
                    bot.activate()
                    break
            else:
                return

    def bot_with_values(self, values):
        """Determine bot index that processed the given pair of values."""
        bots = [bot.index
                for bot in self.bots.values()
                if bot.done and sorted(bot.values) == values]
        if len(bots) == 0:
            raise ValueError('No bot handled the given values.')
        elif len(bots) > 1:
            raise ValueError('Bot cannot be uniquely identified.')
        return bots[0]

    def get_outputs(self, indices):
        """Fetch values stored at the given output indices."""
        return [self.outputs[index].value for index in indices]


def main():
    """Main entry point of puzzle solution."""
    factory = Factory.from_lines(read_input())
    factory.simulate()

    part_one = factory.bot_with_values([17, 61])
    part_two = functools.reduce(operator.mul, factory.get_outputs(range(3)))

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
