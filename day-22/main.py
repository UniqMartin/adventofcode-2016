"""Advent of Code 2016 - Day 22."""

import itertools
import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class Node:
    """Storage nodes with information about their used/available size."""

    # Regular expression for parsing storage node information.
    NODE_REGEXP = re.compile(r'^/dev/grid/node-x(?P<x>\d+)-y(?P<y>\d+)\s+'
                             r'(?P<size>\d+)T\s+(?P<used>\d+)T\s+'
                             r'(?P<avail>\d+)T\s+(?P<used_percent>\d+)%$')

    @classmethod
    def from_line(cls, line):
        """Initialize a storage node from a line from the input file."""
        match = cls.NODE_REGEXP.search(line)
        if match is None:
            raise ValueError('Failed to parse node line in input.')
        return cls((int(match.group('x')), int(match.group('y'))),
                   int(match.group('size')),
                   int(match.group('used')),
                   int(match.group('avail')))

    def __init__(self, position, size, used, avail):
        """"Initialize a storage node from its properties."""
        self.position = position
        self.size = size
        self.used = used
        self.avail = avail

    def move_to(self, other):
        """Move the data of this node to a different node (unchecked)."""
        data_size = self.used
        self.used = 0
        self.avail += data_size
        other.used += data_size
        other.avail -= data_size


class Grid:
    """Rectangular grid with extents and blocked nodes."""

    def __init__(self, max_x, max_y, blocked):
        """Initialize a grid of nodes."""
        self.max_x = max_x
        self.max_y = max_y
        self.blocked = blocked

    def is_blocked(self, x, y):
        """Check if node at the given coordinate is blocked."""
        return (x, y) in self.blocked

    def shortest_path(self, origin, target_location):
        """Find the shortest path between origin and target."""
        marked = {}
        for _distance, wave in self.__walk(marked, origin):
            if target_location in wave:
                return self.__path(marked, target_location)

    def __neighbors(self, x, y):
        """Yield all nodes accessible from the node at the given location."""
        if (x > 0) and not self.is_blocked(x - 1, y):
            yield x - 1, y
        if (x < self.max_x) and not self.is_blocked(x + 1, y):
            yield x + 1, y
        if (y > 0) and not self.is_blocked(x, y - 1):
            yield x, y - 1
        if (y < self.max_y) and not self.is_blocked(x, y + 1):
            yield x, y + 1

    def __path(self, marked, target):
        """Reconstruct a path through the grid from the marked nodes."""
        path = [target]

        distance = marked[target]
        position = target
        while distance > 0:
            distance -= 1
            position = next(neighbor
                            for neighbor in self.__neighbors(*position)
                            if marked.get(neighbor, -1) == distance)
            path.insert(0, position)

        return path

    def __walk(self, marked, origin):
        """Yield waves while walking/marking the grid using Lee algorithm."""
        marked[origin] = 0

        old_wave = {origin}
        new_wave = set()
        for distance in itertools.count(1):
            yield distance - 1, old_wave

            for position in old_wave:
                for neighbor in self.__neighbors(*position):
                    if neighbor not in marked:
                        marked[neighbor] = distance
                        new_wave.add(neighbor)

            if len(new_wave) == 0:
                raise RuntimeError('Search space exhausted.')

            # Prepare for next wave.
            old_wave = new_wave
            new_wave = set()


def viable_pair(node_a, node_b):
    """Check if two nodes are a viable pair of storage nodes."""
    if (node_a is node_b) or (node_a.used == 0):
        return False
    return node_a.used <= node_b.avail


def viable_pairs(nodes):
    """Determine the number of viable pairs among storage nodes."""
    node_pairs = itertools.product(nodes, repeat=2)
    return sum(1 for node_pair in node_pairs if viable_pair(*node_pair))


def build_moves(origin, goal, empty_left_of_goal):
    """Yield moves that make up the solution."""
    # Virtually move empty node next to goal by shifting data on its path.
    for source, target in zip(empty_left_of_goal[1:], empty_left_of_goal):
        yield source, target

    # Move goal once to the left.
    yield goal, empty_left_of_goal[-1]

    # Take turns virtually moving the empty node (from being to the right of
    # the goal to being left of it) and moving the goal one step left. Repeat
    # until the goal data arrives at the origin.
    for x in reversed(range(origin[0] + 1, goal[0])):
        # Virtually move empty node.
        yield (x + 1, 1), (x + 1, 0)
        yield (x, 1), (x + 1, 1)
        yield (x - 1, 1), (x, 1)
        yield (x - 1, 0), (x - 1, 1)

        # Move goal once to the left.
        yield (x, 0), (x - 1, 0)


def fewest_steps(nodes):
    """Determine the fewest steps needed to move goal data to origin.

    This operates on various assumptions and will break down if they are not
    met by the input data. The path between the origin and the node is expected
    to be unobstructed. The same is assumed for the second row (that is needed
    for moving around unrelated data). Nodes that don't have a viable pair are
    considered to be not movable (meaning they are an obstruction in a possible
    path for data movements). Only one node can be empty and it is assumed to
    have enough free space to hold data from any movable (the same is assumed
    for any other pair of movable nodes).

    All those assumptions are used to construct a relatively simple solution
    strategy that is then validated to avoid producing invalid results.
    """
    max_x = max(node.position[0] for node in nodes)
    max_y = max(node.position[1] for node in nodes)
    if (max_x + 1) * (max_y + 1) != len(nodes):
        raise ValueError('Given nodes do not span a rectangular grid.')

    # Convert node list to dictionary for easier access.
    nodes = {node.position: node for node in nodes}

    # Determine positions of special nodes.
    origin = (0, 0)
    goal = (max_x, 0)
    empty = None
    blocked = []
    for position, node in nodes.items():
        if node.used != 0:
            continue
        if empty is not None:
            raise ValueError('Expected only one node to be empty.')
        empty = position
    if empty is None:
        raise ValueError('Expected one node to be empty but none found.')
    for position, node in nodes.items():
        if position == empty:
            continue
        if not viable_pair(node, nodes[empty]):
            blocked.append(position)

    # Check that path between origin and goal is unobstructed.
    for y, x in itertools.product(range(2), range(origin[0], goal[0] + 1)):
        if (x, y) in blocked:
            raise ValueError('Path between origin and goal is obstructed.')

    # Check that origin and goal have sufficient horizontal separation.
    if goal[0] - origin[0] < 2:
        raise ValueError('Origin and goal are too close.')

    # Determine path from empty node to left neighbor of goal.
    left_of_goal = (goal[0] - 1, goal[1])
    grid = Grid(max_x, max_y, blocked)
    empty_left_of_goal = grid.shortest_path(empty, left_of_goal)

    # Construct list of from-to pairs of moves of solution and validate it.
    moves = list(build_moves(origin, goal, empty_left_of_goal))
    for source, target in moves:
        source_node = nodes[source]
        target_node = nodes[target]
        if not viable_pair(source_node, target_node):
            raise ValueError('Failed to find valid solution.')
        source_node.move_to(target_node)

    return len(moves)


def main():
    """Main entry point of puzzle solution."""
    nodes = [Node.from_line(line) for line in read_input()[2:]]

    part_one = viable_pairs(nodes)
    part_two = fewest_steps(nodes)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
