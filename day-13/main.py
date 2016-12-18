"""Advent of Code 2016 - Day 13."""

import itertools


class Maze:
    """Maze with layout computed from the office designer's favorite number."""

    def __init__(self, favorite_number):
        """Initialize a maze."""
        self.favorite_number = favorite_number

    def is_wall(self, x, y):
        """Check if there is a wall at the given coordinate."""
        value = x * x + 3 * x + 2 * x * y + y + y * y + self.favorite_number
        return bin(value).count('1') % 2 == 1

    def print(self, columns, rows, path=None):
        """Print the first few columns and rows of the maze."""
        for y in range(rows):
            line = ['.'] * columns
            for x in range(columns):
                if self.is_wall(x, y):
                    line[x] = '#'
                elif (path is not None) and ((x, y) in path):
                    line[x] = 'O'
            print(''.join(line))

    def shortest_path(self, origin, target_location):
        """Find the shortest path between origin and target."""
        marked = {}
        for _distance, wave in self.__walk(marked, origin):
            if target_location in wave:
                return self.__path(marked, target_location)

    def distinct_locations(self, origin, target_distance):
        """Find all locations reachable within a given number of steps."""
        marked = {}
        for distance, _wave in self.__walk(marked, origin):
            if distance == target_distance:
                return marked.keys()

    def __neighbors(self, x, y):
        """Yield all open spaces reachable from the given location."""
        if (x > 0) and not self.is_wall(x - 1, y):
            yield x - 1, y
        if not self.is_wall(x + 1, y):
            yield x + 1, y
        if (y > 0) and not self.is_wall(x, y - 1):
            yield x, y - 1
        if not self.is_wall(x, y + 1):
            yield x, y + 1

    def __path(self, marked, target):
        """Reconstruct a path through the maze from the marked nodes."""
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
    INPUT_FAVORITE_NUMBER = 1364
    INPUT_TARGET_LOCATION = (31, 39)
    INPUT_TARGET_DISTANCE = 50

    maze = Maze(INPUT_FAVORITE_NUMBER)

    part_one = maze.shortest_path((1, 1), INPUT_TARGET_LOCATION)
    part_two = maze.distinct_locations((1, 1), INPUT_TARGET_DISTANCE)

    print('Part One: {}'.format(len(part_one) - 1))  # Don't count origin.
    print('Part Two: {}'.format(len(part_two)))


if __name__ == '__main__':
    main()
