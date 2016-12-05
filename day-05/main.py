"""Advent of Code 2016 - Day 5."""

import hashlib
import itertools


def md5_with_prefix(door_id, prefix):
    """Yield MD5 hashes generated from a door ID and an increasing integer."""
    md5_input = hashlib.md5(door_id)

    for number in itertools.count():
        md5 = md5_input.copy()
        md5.update(str(number).encode('ascii'))
        if md5.hexdigest().startswith(prefix):
            yield md5.hexdigest()


def first_door_password(door_id):
    """Determine the password for the first door and a given door ID."""
    prefix_len = 5
    prefix = '0' * prefix_len

    password = []
    for md5 in itertools.islice(md5_with_prefix(door_id, prefix), 8):
        password.append(md5[prefix_len])  # The character after the prefix.

    return ''.join(password)


def second_door_password(door_id):
    """Determine the password for the second door and a given door ID."""
    prefix_len = 5
    prefix = '0' * prefix_len

    password = list('_' * 8)
    for md5 in md5_with_prefix(door_id, prefix):
        # Skip, if position is out of range (outside the range 0 to 7).
        position = md5[prefix_len]
        if not ('0' <= position <= '7'):
            continue

        # Skip, if position in password is already filled.
        position = ord(position) - ord('0')
        if password[position] != '_':
            continue

        # Update password and check if it is complete (has no underscores).
        password[position] = md5[prefix_len + 1]
        if '_' not in password:
            break

    return ''.join(password)


def main():
    """Main entry point of puzzle solution."""
    INPUT_DOOR_ID = b'ojvtpuvg'

    part_one = first_door_password(INPUT_DOOR_ID)
    part_two = second_door_password(INPUT_DOOR_ID)

    print('Part One: {}'.format(part_one))
    print('Part Two: {}'.format(part_two))


if __name__ == '__main__':
    main()
