"""Advent of Code 2016 - Day 14."""

import hashlib
import itertools
import re


class CachedHasher:
    """Cached MD5 hasher."""

    def __init__(self, seed):
        """Initialize a cached MD5 hasher with a seed."""
        self.cache_size = 4096
        self.cache_digest = [''] * self.cache_size
        self.cache_number = [-1] * self.cache_size
        self.seed = seed

    def generate(self, start_with=0):
        """Yield MD5 hashes generated from a seed and an increasing integer."""
        md5_input = hashlib.md5(self.seed)

        for number in itertools.count(start_with):
            cache_key = number % self.cache_size
            if self.cache_number[cache_key] == number:
                yield number, self.cache_digest[cache_key]
                continue

            md5 = md5_input.copy()
            md5.update(str(number).encode('ascii'))
            digest = self._transform_digest(md5.hexdigest())

            self.cache_digest[cache_key] = digest
            self.cache_number[cache_key] = number

            yield number, digest

    def _transform_digest(self, digest):
        """Transform digest before yielding (identity transformation here)."""
        return digest


class StretechedHasher(CachedHasher):
    """Stretched (and cached) MD5 hasher."""

    def __init__(self, seed, extra_rounds):
        """Initialize a stretched MD5 hasher with seed and extra rounds."""
        CachedHasher.__init__(self, seed)
        self.extra_rounds = extra_rounds

    def _transform_digest(self, digest):
        """Transform generated digest by applying some extra rounds of MD5."""
        for _round in range(self.extra_rounds):
            digest = hashlib.md5(digest.encode('ascii')).hexdigest()
        return digest


def md5_is_key(hasher, character, number):
    """Check whether a candidate hash is indeed a valid key."""
    start_with = number + 1
    token = character * 5
    check_iterator = hasher.generate(start_with=start_with)
    for check_number, check_md5 in itertools.islice(check_iterator, 1000):
        if token in check_md5:
            return True
    return False


def otp_last_index(hasher, num_keys):
    """Determine number of hash for last key in one-time pad."""
    keys = []

    for number, md5 in hasher.generate():
        match = re.search(r'([0-9a-f])\1{2}', md5)
        if match is None:
            continue

        if md5_is_key(hasher, match.group(1), number):
            keys.append((number, md5))
            if len(keys) >= num_keys:
                break

    return keys[num_keys - 1][0]


def main():
    """Main entry point of puzzle solution."""
    INPUT_SEED = b'cuanljph'
    INPUT_KEYS = 64

    part_one = CachedHasher(INPUT_SEED)
    part_two = StretechedHasher(INPUT_SEED, extra_rounds=2016)

    print('Part One: {}'.format(otp_last_index(part_one, INPUT_KEYS)))
    print('Part Two: {}'.format(otp_last_index(part_two, INPUT_KEYS)))


if __name__ == '__main__':
    main()
