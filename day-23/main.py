"""Advent of Code 2016 - Day 23."""

import re
from copy import deepcopy
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


class ToggleInstruction(Exception):
    """Exception raised by toggle instruction to cause program mutation."""

    def __init__(self, address):
        """Initialize a toggle instruction exception."""
        self.address = address


class Instruction:
    """Machine instruction with instruction name and arguments."""

    def __init__(self, name, *args):
        """Initialize an instruction from its name and arguments."""
        self.name = name
        self.arguments = [self.__parse_value(arg) for arg in args]

        # Per-instruction statistics for debugging.
        self.executed = 0
        self.toggled = 0

        # Optimization-related properties.
        self.optimized = False
        self.chunk_head = False

    def execute(self, state):
        """Execute the instruction and update machine state."""
        self.executed += 1
        if self.name == 'cpy':
            source, target = self.arguments
            if isinstance(target, str):
                state[target] = self.__fetch_value(state, source)
        elif self.name == 'dec':
            register = self.arguments[0]
            if isinstance(register, str):
                state[register] -= 1
        elif self.name == 'inc':
            register = self.arguments[0]
            if isinstance(register, str):
                state[register] += 1
        elif self.name == 'jnz':
            value, offset = self.arguments
            if self.__fetch_value(state, value) != 0:
                address = state.ip + self.__fetch_value(state, offset)
                raise JumpToInstruction(address)
        elif self.name == 'mul':
            source, target = self.arguments
            if isinstance(target, str):
                state[target] *= self.__fetch_value(state, source)
        elif self.name == 'nop':
            pass  # Do nothing.
        elif self.name == 'tgl':
            address = state.ip + self.__fetch_value(state, self.arguments[0])
            state.ip += 1
            raise ToggleInstruction(address)
        else:
            raise ValueError('Unrecognized instruction: {}.'.format(self.name))

        # For almost all instructions, just move to the next instruction.
        state.ip += 1

    def toggle(self):
        """Transform the instruction when toggled."""
        if self.optimized:
            raise ValueError('Cannot toggle an optimized instruction.')
        self.toggled += 1
        if len(self.arguments) == 1:
            self.name = 'dec' if self.name == 'inc' else 'inc'
        else:  # Two-argument instructions.
            self.name = 'cpy' if self.name == 'jnz' else 'jnz'

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
    """Program with (extended) assembunny code."""

    # Regular expressions for parsing all supported instructions.
    INSTRUCTION_REGEXPS = list(map(re.compile, [
        r'^(nop)$',
        r'^(dec|inc|tgl) (-?\d+|[a-d])$',
        r'^(cpy|jnz|mul) (-?\d+|[a-d]) (-?\d+|[a-d])$',
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

    def optimize(self):
        """Optimize the program to speed up execution."""
        pattern = [
            r'cpy (?P<a>[a-d]) (?P<d>[a-d])',
            r'cpy 0 (?P=a)',
            r'cpy (?P<b>[a-d]) (?P<c>[a-d])',
            r'inc (?P=a)',
            r'dec (?P=c)',
            r'jnz (?P=c) -2',
            r'dec (?P=d)',
            r'jnz (?P=d) -5',
        ]
        replacement = [
            'mul {b} {a}',
            # Set (now unused) counters to expected values.
            'cpy 0 {c}',
            'cpy 0 {d}',
            # Pad code to avoid recalculation of jump offsets.
            'nop',
            'nop',
            'nop',
            'nop',
            'nop',
        ]

        # We currently only have a single pattern: Replace an iterative nested
        # loop that multiplies two registers with a direct multiplication.
        lines = [str(instruction) for instruction in self.code]
        pattern_re = re.compile('\n'.join(pattern))
        for offset in range(len(lines) - len(pattern) + 1):
            chunk = '\n'.join(lines[offset:offset + len(pattern)])
            match = pattern_re.fullmatch(chunk)
            if match is None:
                continue
            fields = match.groupdict()
            if len(set(fields.values())) != len(fields):
                continue
            for index in range(len(pattern)):
                line = replacement[index].format(**fields)
                self.code[offset + index] = self._parse_line(line)
                self.code[offset + index].optimized = True
            self.code[offset].chunk_head = True
            return

        # Treat failed optimization as a fatal error to more easily find
        # programs that don't match the pattern we've derived from our
        # puzzle input. Otherwise program will be too slow in second part.
        raise ValueError('Failed to optimize program.')

    def run(self, initial_state=None, stats=False):
        """Run a program and return machine state after execution finishes."""
        # Copy code to avoid impact on later runs.
        code = deepcopy(self.code)

        state = MachineState(initial=initial_state)
        count = 0
        while 0 <= state.ip < len(code):
            count += 1
            try:
                code[state.ip].execute(state)
            except JumpToInstruction as jump:
                target = code[jump.address]
                if target.optimized and not target.chunk_head:
                    raise ValueError('Cannot jump into an optimized chunk.')
                state.ip = jump.address
            except ToggleInstruction as toggle:
                if 0 <= toggle.address < len(code):
                    code[toggle.address].toggle()

        if stats:
            print('  # exec\'ed toggled instruction')
            print('--- ------- ------- -----------')
            for line, instruction in enumerate(code):
                print('{:3} {:7} {:7} {}'.format(line + 1,
                                                 instruction.executed,
                                                 instruction.toggled,
                                                 instruction.name))
            print('--- ------- ------- -----------')
            print('    {: 7} = total'.format(count))
            print()

        return state


def main():
    """Main entry point of puzzle solution."""
    program = Program.from_lines(read_input())
    program.optimize()

    part_one = program.run(initial_state={'a': 7})['a']
    part_two = program.run(initial_state={'a': 12})['a']

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
