"""Advent of Code 2016 - Day 25."""

import itertools
import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


class MachineState:
    """Machine state with instruction pointer and arithmetic registers."""

    def __init__(self, initial=None):
        """Initialize machine state, possibly also setting some registers."""
        self.ip = 0
        self.registers = {register: 0 for register in ['a', 'b', 'c', 'd']}
        if initial is not None:
            self.registers.update(initial)

    def __getitem__(self, key):
        """Simplify read access to registers."""
        return self.registers[key]

    def __setitem__(self, key, value):
        """Simplify write access to registers."""
        if key not in self.registers:
            raise KeyError
        self.registers[key] = value


class JumpToInstruction(Exception):
    """Exception raised by jump instruction to cause non-linear execution."""

    def __init__(self, address):
        """Initialize a jump instruction exception."""
        self.address = address


class OutputInstruction(Exception):
    """Exception raised by output instruction to yield output data."""

    def __init__(self, value):
        """Initialize an output instruction exception."""
        self.value = value


class Instruction:
    """Machine instruction with instruction name and arguments."""

    def __init__(self, name, *args):
        """Initialize an instruction from its name and arguments."""
        self.name = name
        self.arguments = [self.__parse_value(arg) for arg in args]

    def execute(self, state):
        """Execute the instruction and update machine state."""
        if self.name == 'cpy':
            source, target = self.arguments
            state[target] = self.__fetch_value(state, source)
        elif self.name == 'dec':
            register = self.arguments[0]
            state[register] -= 1
        elif self.name == 'inc':
            register = self.arguments[0]
            state[register] += 1
        elif self.name == 'jnz':
            value, offset = self.arguments
            if self.__fetch_value(state, value) != 0:
                address = state.ip + self.__fetch_value(state, offset)
                raise JumpToInstruction(address)
        elif self.name == 'out':
            value = self.arguments[0]
            value = self.__fetch_value(state, value)
            state.ip += 1
            raise OutputInstruction(value)
        else:
            raise ValueError('Unrecognized instruction: {}.'.format(self.name))

        # For almost all instructions, just move to the next instruction.
        state.ip += 1

    def __fetch_value(self, state, value):
        """Fetch a register/literal instruction argument."""
        if isinstance(value, str):
            return state[value]
        else:
            return value

    def __parse_value(self, value):
        """Parse a register/literal instruction argument from string."""
        try:
            return int(value)
        except ValueError:
            return value

    def __str__(self):
        """Provide a human-readable representation of the instruction."""
        return '{} {}'.format(self.name, ' '.join(map(str, self.arguments)))


class Program:
    """Program with assembunny code for generating a clock signal."""

    # Regular expressions for parsing all supported instructions.
    INSTRUCTION_REGEXPS = list(map(re.compile, [
        r'^(dec|inc|out) (-?\d+|[a-d])$',
        r'^(cpy|jnz) (-?\d+|[a-d]) (-?\d+|[a-d])$',
    ]))

    @classmethod
    def from_lines(cls, lines):
        """Initialize a program from lines from the input file."""
        return cls([cls._parse_line(line) for line in lines])

    @classmethod
    def _parse_line(cls, line):
        """Parse a line of the program code and return instruction object."""
        for regexp in cls.INSTRUCTION_REGEXPS:
            match = regexp.search(line)
            if match is not None:
                return Instruction(*match.groups())

        raise ValueError('Unrecognized instruction: {}'.format(line))

    def __init__(self, code=None):
        """Initialize an empty program or populate it with the given code."""
        self.code = code or []

    def run(self, initial_state=None):
        """Run a program and return machine state after execution finishes."""
        state = MachineState(initial=initial_state)
        while 0 <= state.ip < len(self.code):
            try:
                self.code[state.ip].execute(state)
            except JumpToInstruction as jump:
                state.ip = jump.address
            except OutputInstruction as output:
                yield output.value


def clock_signal_seed(program):
    """Find the lowest seed value that results in a valid clock signal.

    Experimentation has shown the signal has a period of length 12, thus this
    is the longest output length that we need to check to be confident of the
    determined seed value. (Assuming this isn't exactly a good idea, but I'm
    currently too lazy to find a cleaner and more robust solution.)
    """
    check_limit = 12
    for seed in itertools.count(1):
        signal_generator = program.run(initial_state={'a': seed})
        for index, signal in zip(range(check_limit), signal_generator):
            if index % 2 != signal:
                break
        else:
            return seed


def main():
    """Main entry point of puzzle solution."""
    program = Program.from_lines(read_input())

    part_one = clock_signal_seed(program)

    print('Part One: {}'.format(part_one))
    print('Part Two: N/A')


if __name__ == '__main__':
    main()
