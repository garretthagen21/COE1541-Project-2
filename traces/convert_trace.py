import argparse
import random


def convert_to_base(decimal_number, base, addr_size):
    DIGITS = '0123456789abcdef'
    remainder_stack = []

    while decimal_number > 0:
        remainder = decimal_number % base
        remainder_stack.append(remainder)
        decimal_number = decimal_number // base

    new_digits = []
    while remainder_stack:
        new_digits.append(DIGITS[remainder_stack.pop()])

    # Hack to make binary numbers addr_size bits
    if base == 2:
        while len(new_digits) < addr_size:
            new_digits.insert(0, '0')

    return ''.join(new_digits)


def coin_flip(prob=0.5):
    prob = min(1.0, max(0.0, prob))
    return random.randint(1, 100) <= prob * 100


def convert_trace_file(out_file, convert_file, number_base):
    wFile = open(out_file, 'w+')
    rFile = open(convert_file, 'r')

    line_num = 1
    for line in rFile.readlines():
        tokens = line.split()
        # Add a time if none available
        if len(tokens) < 3:
            tokens.append(str(line_num))

        # Convert to int if neccessary
        if number_base != 10:
            tokens[1] = str(int(tokens[1], number_base))

        # move to lower case
        tokens[0] = tokens[0].lower()

        # Rejoin lines
        new_line = ' '.join(tokens)

        wFile.write(new_line + "\n")

        line_num += 1

    rFile.close()
    wFile.close()


if __name__ == "__main__":
    # Add our program arguments
    parser = argparse.ArgumentParser(description='Create a trace file for testing cache accesses')
    parser.add_argument('-f', '--filename', dest='file_name', default='default.trace', type=str,
                        help="Filename for output tracefile")
    parser.add_argument('-c', '--convertfile', dest='convert_file', default='', type=str,
                        help="Filename for input tracefile")

    parser.add_argument('-b', '--base', dest='number_base', default=2, type=int,
                        help="Number base (e.g. decimal = 10, binary = 2, hex = 16)")

    # Parse the arguments
    args = parser.parse_args()

    # Verify they are correct
    convert_trace_file(args.file_name, args.convert_file, args.number_base)

    print("Done!")
