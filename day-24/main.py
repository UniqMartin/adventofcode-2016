"""Advent of Code 2016 - Day 24."""

import itertools
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class Maze:
    """Maze of air ducts walked by robot."""

    @classmethod
    def from_lines(cls, lines):
        """Initialize a maze from lines from the input file."""
        width = len(lines[0])
        height = len(lines)
        walls = set()
        pois = {}
        for y, line in enumerate(lines):
            for x, cell in enumerate(line):
                if cell == '#':
                    walls.add((x, y))
                elif cell != '.':
                    poi = int(cell)
                    pois[poi] = (x, y)
        return cls(width, height, walls, pois)

    def __init__(self, width, height, walls, pois):
        """Initialize a maze."""
        self.width = width
        self.height = height
        self.walls = walls
        self.pois = pois
        self.poi_distances = {}

    def shortest_route(self, with_return=False):
        """Determine the shortest route length for visiting all POIs."""
        return min(self.__routes(with_return))

    def is_wall(self, x, y):
        """Check if there is a wall at the given coordinate."""
        return (x, y) in self.walls

    def poi_distance(self, origin, target):
        """Determine the shortest distance between two POIs (cached)."""
        if origin == target:
            return 0
        if origin > target:
            origin, target = target, origin

        distance = self.poi_distances.get((origin, target))
        if distance is not None:
            return distance

        distance = self.__distance(self.pois[origin], self.pois[target])
        self.poi_distances[(origin, target)] = distance
        return distance

    def __distance(self, origin, target):
        """Determine the shortest distance between origin and target."""
        marked = {}
        for distance, wave in self.__walk(marked, origin):
            if target in wave:
                return distance

    def __routes(self, with_return):
        """Yield step counts of all possible routes through maze."""
        nonzeo_pois = list(filter(None, self.pois.keys()))

        for path in itertools.permutations(nonzeo_pois):
            steps = self.poi_distance(0, path[0])
            for i, j in zip(path, path[1:]):
                steps += self.poi_distance(i, j)
            if with_return:
                steps += self.poi_distance(path[-1], 0)
            yield steps

    def __neighbors(self, x, y):
        """Yield all open spaces reachable from the given location."""
        if (x > 0) and not self.is_wall(x - 1, y):
            yield x - 1, y
        if (x < self.width - 1) and not self.is_wall(x + 1, y):
            yield x + 1, y
        if (y > 0) and not self.is_wall(x, y - 1):
            yield x, y - 1
        if (y < self.height - 1) and not self.is_wall(x, y + 1):
            yield x, y + 1

    def __walk(self, marked, origin):
        """Yield waves while walking/marking the maze using Lee algorithm."""
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


def main():
    """Main entry point of puzzle solution."""
    maze = Maze.from_lines(read_input())

    part_one = maze.shortest_route()
    part_two = maze.shortest_route(with_return=True)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
