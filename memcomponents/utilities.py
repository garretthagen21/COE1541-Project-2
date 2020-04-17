import math
from prettytable import PrettyTable
import sys


def show_error_and_exit(error_string, code=1):
    print("\n[Error] " + error_string + " Exiting program...\n")
    sys.exit(code)


def draw_vertical_line(height, indent=10):
    line = ""
    indent_str = ""
    # Make indent string
    for i in range(indent):
        indent_str += " "
    # Draw arrow pointing down
    for i in range(height):
        line += ("\n" if i > 0 else "") + indent_str + "|"
    return line


def bits_required(num):
    return math.ceil(math.log2(num))


def adjust_to_standard_size(bytes):
    return 2 ** bits_required(bytes)


# Convenience dict lookup
def dict_lookup(dict, key):
    try:
        return dict[key]
    except KeyError:
        return None
