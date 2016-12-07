"""Advent of Code 2016 - Day 7."""

import re
from pathlib import Path


def read_input():
    """Read input file and split into individual lines returned as a list."""
    return Path(__file__).with_name('input.txt').read_text().splitlines()


def split_address(address):
    """Split address into two lists of supernet and hypernet sequences."""
    sequences = re.split(r'(\[.*?\])', address)
    supernet = [s for s in sequences if s[0] != '[']
    hypernet = [s[1:-1] for s in sequences if s[0] == '[']
    return supernet, hypernet


def contains_abba(address):
    """Check if the address contains an Autonomous Bridge Bypass Annotation."""
    return re.search(r'(.)(?!\1)(.)\2\1', address) is not None


def all_triples(sequences):
    """Return a set of all triples (ABAs or BABs) found in sequences."""
    triple_re = re.compile(r'(.)(?!\1)(.)\1')
    triples = set()
    for sequence in sequences:
        for pos in range(len(sequence) - 2):
            match = triple_re.match(sequence, pos=pos)
            if match:
                triples.add(match.group(0))
    return triples


def bab_to_aba(bab):
    """Transform a BAB to the matching ABA."""
    return bab[1] + bab[0:2]


def has_tls_support(address):
    """Check if the address supports TLS (transport-layer snooping)."""
    if not contains_abba(address):
        return False
    _supernet, hypernet = split_address(address)
    if any(filter(contains_abba, hypernet)):
        return False
    return True


def has_ssl_support(address):
    """Check if the address supports SSL (super-secret listening)."""
    supernet, hypernet = split_address(address)
    aba = all_triples(supernet)
    bab = all_triples(hypernet)
    return not aba.isdisjoint(set(map(bab_to_aba, bab)))


def count_if(predicate, iterable):
    """Count the number of items of an iterable that satisfy predicate."""
    return sum(1 for item in iterable if predicate(item))


def main():
    """Main entry point of puzzle solution."""
    addresses = read_input()

    part_one = count_if(has_tls_support, addresses)
    part_two = count_if(has_ssl_support, addresses)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
