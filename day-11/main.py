"""Advent of Code 2016 - Day 11."""

import itertools
import operator
import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


def test_input():
    """Provide example input from puzzle description (for testing)."""
    return [
        ('The first floor contains a hydrogen-compatible microchip and a '
         'lithium-compatible microchip.'),
        'The second floor contains a hydrogen generator.',
        'The third floor contains a lithium generator.',
        'The fourth floor contains nothing relevant.',
    ]


class Item:
    """Generic item that can be placed in a floor of the facility."""

    def __init__(self, element, label=None, column=None):
        """Initialize an item with its associated element name."""
        self.element = element
        self.label = label
        self.column = column

    def update_label(self, prefix):
        """Update label from an element prefix and the class name initial."""
        suffix = self.__class__.__name__[0]
        self.label = prefix + suffix

    def __eq__(self, other):
        """Compare items for equality with each other."""
        return (type(self) == type(other)) and (self.element == other.element)


class Generator(Item):
    """Generator item."""


class Microchip(Item):
    """Microchip item."""

    def __init__(self, *args, **kwargs):
        """Initialize a microchip item."""
        Item.__init__(self, *args, **kwargs)
        self.generator = None


class Facility:
    """Facility with floors, an elevator, and items placed on those floors."""

    # Mapping from spelled-out floor name to a zero-based floor index.
    FLOOR_MAP = {
        'first': 0,
        'second': 1,
        'third': 2,
        'fourth': 3,
    }

    # Regular expression for parsing floor description.
    FLOOR_REGEXP = re.compile(r'^The (\w+) floor contains (.+)\.$')

    # Regular expression for splitting floor contents into a list of items.
    ITEMS_SPLIT_REGEXP = re.compile(r'(?:,? and |, )')

    # Regular expression for parsing generator items.
    GENERATOR_REGEXP = re.compile(r'^a (\w+) generator$')

    # Regular expression for parsing microchip items.
    MICROCHIP_REGEXP = re.compile(r'^a (\w+)-compatible microchip$')

    @classmethod
    def from_lines(cls, lines, with_extras=True):
        """Initialize a facility from lines from the input file."""
        facility = cls()

        done = [False for _ in facility.floors]
        for line in lines:
            floor, items = cls.FLOOR_REGEXP.search(line).groups()
            floor = facility.__floor_index(floor)
            items = cls.ITEMS_SPLIT_REGEXP.split(items)
            facility.__add_floor(floor, items)
            done[floor] = True

        if not all(done):
            raise ValueError('Some floors were left unpopulated.')

        # Add some extra generators and microchips (as needed in part two).
        if with_extras:
            for element in ['elerium', 'dilithium']:
                facility.__add_item(0, Generator(element))
                facility.__add_item(0, Microchip(element))

        # Post-process items list after having populated it completely.
        facility.__update_labels()
        facility.__assign_columns()
        facility.__assign_generators()

        return facility

    def __init__(self, elevator=None, floors=None, items=None):
        """Initialize a (usually empty) facility."""
        self.elevator = elevator or 0  # Always start in 1st floor.
        self.floors = floors or [set() for _ in range(4)]  # Always 4 floors.
        self.items = items or []

    def solved(self):
        """Check whether facility is in a solved state (all items on top)."""
        return len(self.floors[-1]) == len(self.items)

    def id(self):
        """Provide string that compactly represents the current state."""
        item2floor = [None] * len(self.items)
        for floor_index, floor_items in enumerate(self.floors):
            for item_index in floor_items:
                item2floor[item_index] = floor_index
        item_spec = ','.join('{}:{}'.format(item.label, floor)
                             for floor, item in zip(item2floor, self.items))
        return '{};{}'.format(self.elevator, item_spec)

    def options(self):
        """Yield valid states that can result from the current one."""
        ud = [delta
              for delta in [+1, -1]
              if 0 <= self.elevator + delta < len(self.floors)]
        pool = self.floors[self.elevator]
        pool = list(itertools.chain(itertools.combinations(pool, 1),
                                    itertools.combinations(pool, 2)))
        pool = [set(move) for move in pool]

        for delta in ud:
            old_floor = self.floors[self.elevator]
            new_floor = self.floors[self.elevator + delta]
            for move in pool:
                old_moved = old_floor - move
                if not self.__valid_floor(old_moved):
                    continue

                new_moved = new_floor | move
                if not self.__valid_floor(new_moved):
                    continue

                floors = self.floors[:]
                floors[self.elevator] = old_moved
                floors[self.elevator + delta] = new_moved

                yield Facility(self.elevator + delta, floors, self.items)

    def __str__(self):
        """Provide a human-readable representation of a facility."""
        num_columns = len(self.items)
        placeholder = '.' * len(self.items[0].label)
        lines = []
        for floor_index, floor in enumerate(self.floors):
            line = 'F{} '.format(floor_index + 1)
            if floor_index == self.elevator:
                line += 'E '
            else:
                line += '. '
            items = [placeholder] * num_columns
            for item_index in floor:
                item = self.items[item_index]
                items[item.column] = item.label
            line += ' '.join(items)
            lines.insert(0, line)
        return '\n'.join(lines)

    def __add_floor(self, floor, items):
        """Populate a floor with items provided as a list of strings."""
        for item in items:
            generator = self.GENERATOR_REGEXP.search(item)
            if generator is not None:
                self.__add_item(floor, Generator(generator.group(1)))
                continue

            microchip = self.MICROCHIP_REGEXP.search(item)
            if microchip is not None:
                self.__add_item(floor, Microchip(microchip.group(1)))
                continue

            if item != 'nothing relevant':
                raise ValueError('Unexpected item: {}'.format(item))

    def __add_item(self, floor, item):
        """Add an item to a floor."""
        try:
            index = self.items.index(item)
        except ValueError:
            index = len(self.items)
            self.items.append(item)
        self.floors[floor].add(index)

    def __assign_columns(self):
        """Assign column indices to items for pretty-printing."""
        label_getter = operator.attrgetter('label')
        for column, item in enumerate(sorted(self.items, key=label_getter)):
            item.column = column

    def __assign_generators(self):
        """Associate microchips with corresponding generators."""
        generators = {item.element: index
                      for index, item in enumerate(self.items)
                      if isinstance(item, Generator)}
        for item in self.items:
            if isinstance(item, Microchip):
                item.generator = generators[item.element]

    def __floor_index(self, name):
        """Map a floor name to a floor index."""
        return self.FLOOR_MAP[name]

    def __update_labels(self):
        """Update item labels to make them unique and as short as possible."""
        elements = {item.element for item in self.items}

        length = 1
        while True:
            prefixes = {element[:length] for element in elements}
            if len(prefixes) == len(elements):
                break
            length += 1

        prefixes = {element: element[:length] for element in elements}
        for item in self.items:
            prefix = prefixes[item.element].capitalize().ljust(length)
            item.update_label(prefix)

    def __valid_floor(self, floor):
        """Check whether given items can coexist with each other on a floor."""
        have_generator = False
        need_generator = False
        for item_index in floor:
            item = self.items[item_index]
            if isinstance(item, Generator):
                have_generator = True
            elif isinstance(item, Microchip) and (item.generator not in floor):
                need_generator = True
        return not (have_generator and need_generator)


class SolutionFoundError(Exception):
    """Exception that indicates a solution has been found."""

    def __init__(self, depth, state):
        """Initialize a solution exception with depth and state."""
        self.depth = depth
        self.state = state


def expand_node(states, depth, facility):
    """Expand one node of the solution tree and return newly created nodes."""
    queue = []

    options = list(facility.options())
    for index, state in enumerate(options):
        if state.solved():
            # Signal that solution was found by throwing an exception.
            raise SolutionFoundError(depth, state)

        state_id = state.id()
        if state_id in states:
            # Never re-process subtrees that have been encountered at a
            # shallower depth. (Duplicate subtrees occur all the time.)
            continue

        states[state_id] = (depth, state)
        queue.append(state_id)

    return queue


def solution_depth(facility):
    """Determine minimal solution depth by doing a breadth-first search."""
    states = {facility.id(): (0, facility)}
    expand_queue = list(states.keys())

    try:
        # Pull nodes that haven't been handled yet from queue until the search
        # space has been exhausted (queue is empty) or a solution is found.
        while len(expand_queue) > 0:
            base_id = expand_queue.pop(0)
            base_depth, base_state = states[base_id]
            new_states = expand_node(states, base_depth + 1, base_state)
            expand_queue.extend(new_states)
        return None
    except SolutionFoundError as solution:
        return solution.depth


def main():
    """Main entry point of puzzle solution."""
    lines = read_input()
    facility_one = Facility.from_lines(lines)
    facility_two = Facility.from_lines(lines, with_extras=True)

    # FIXME: Part two has truly horrible performance characteristics (about
    #        45 minutes CPU time and 6 GB of RAM on my machine). Nevertheless,
    #        it works and I currently can't be bothered to optimize this.
    part_one = solution_depth(facility_one)
    part_two = solution_depth(facility_two)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
