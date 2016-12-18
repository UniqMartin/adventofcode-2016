"""Advent of Code 2016 - Day 12."""

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


class Instruction:
    """Abstract machine instruction with some instruction-independent logic."""

    def execute(self, state):
        """Execute the instruction and update machine state."""
        state.ip += self._execute(state)

    def _fetch_value(self, state, value):
        """Fetch a register/literal instruction argument."""
        if isinstance(value, str):
            return state[value]
        else:
            return value

    def _parse_value(self, value):
        """Parse a register/literal instruction argument from string."""
        try:
            return int(value)
        except ValueError:
            return value


class CopyInstruction(Instruction):
    """Copy instruction."""

    def __init__(self, source, target):
        """Initialize copy instruction with its arguments."""
        self.source = self._parse_value(source)
        self.target = target

    def _execute(self, state):
        """Execute instruction in the context of the current machine state."""
        source = self._fetch_value(state, self.source)
        state[self.target] = source
        return 1

    def __str__(self):
        """Provide a human-readable representation of the instruction."""
        return 'cpy {} {}'.format(self.source, self.target)


class IncrementInstruction(Instruction):
    """Increment or decrement instruction."""

    def __init__(self, register, increment):
        """Initialize increment/decrement instruction with its argument."""
        self.register = register
        self.increment = increment

    def _execute(self, state):
        """Execute instruction in the context of the current machine state."""
        state[self.register] += self.increment
        return 1

    def __str__(self):
        """Provide a human-readable representation of the instruction."""
        if self.increment == +1:
            return 'inc {}'.format(self.register)
        elif self.increment == -1:
            return 'dec {}'.format(self.register)
        else:
            raise ValueError('Cannot stringify for arbitrary increment.')


class JumpIfNotZeroInstruction(Instruction):
    """Jump if not zero instruction."""

    def __init__(self, value, offset):
        """Initialize jump if not zero instruction from its arguments."""
        self.value = self._parse_value(value)
        self.offset = offset

    def _execute(self, state):
        """Execute instruction in the context of the current machine state."""
        if self._fetch_value(state, self.value) != 0:
            return self.offset
        else:
            return 1

    def __str__(self):
        """Provide a human-readable representation of the instruction."""
        return 'jnz {} {}'.format(self.value, self.offset)


class Program:
    """Program with assembunny code."""

    # Regular expression for parsing copy instructions.
    COPY_REGEXP = re.compile(r'^cpy (-?\d+|[a-d]) ([a-d])$')

    # Regular expression for parsing increment/decrement instructions.
    CALC_REGEXP = re.compile(r'^(inc|dec) ([a-d])$')

    # Regular expression for parsing jump if not zero instructions.
    JUMP_REGEXP = re.compile(r'^jnz (-?\d+|[a-d]) (-?\d+)$')

    @classmethod
    def from_lines(cls, lines):
        """Initialize a program from lines from the input file."""
        return cls([cls._parse_line(line) for line in lines])

    @classmethod
    def _parse_line(cls, line):
        """Parse a line of the program code and return instruction object."""
        copy = cls.COPY_REGEXP.search(line)
        if copy is not None:
            return CopyInstruction(*copy.groups())

        calc = cls.CALC_REGEXP.search(line)
        if calc is not None:
            if calc.group(1) == 'inc':
                return IncrementInstruction(calc.group(2), +1)
            else:
                return IncrementInstruction(calc.group(2), -1)

        jump = cls.JUMP_REGEXP.search(line)
        if jump is not None:
            return JumpIfNotZeroInstruction(jump.group(1),
                                            int(jump.group(2)))

        raise ValueError('Unrecognized instruction: {}'.format(line))

    def __init__(self, code=None):
        """Initialize an empty program or populate it with the given code."""
        self.code = code or []

    def run(self, initial_state=None):
        """Run a program and return machine state after execution finishes."""
        state = MachineState(initial=initial_state)
        while 0 <= state.ip < len(self.code):
            self.code[state.ip].execute(state)
        return state


def main():
    """Main entry point of puzzle solution."""
    program = Program.from_lines(read_input())

    part_one = program.run()['a']
    part_two = program.run(initial_state={'c': 1})['a']

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
