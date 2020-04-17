#!/usr/bin/env python3

import ast
import time
import argparse
import os
from memcomponents.utilities import *
from memcomponents.access_sequence import AccessSequence
from memcomponents.heirarchy import *


class CacheSimulator(object):
    def __init__(self, sequence, heirarchy):
        self.sequence = sequence
        self.heirarchy = heirarchy

    def run(self, debug=1):
        # Record execution time
        start_time = time.time()

        # Execute the memory trace
        for mem_access in self.sequence:
            self.heirarchy.access(mem_access)

            if debug > 1:
                print("\n\n<<<<<<<<<<< Instruction Access >>>>>>>>>>>>>>")
                print("\n" + str(mem_access))
                print("\n" + str(cache_heirarchy))

        if debug > 0:
            print("\n\n************** Final Results ******************")
            print("\n" + str(self.heirarchy) + "\n")
            print("\n" + str(self.sequence) + "\n")

            # Write our execution time
            hours, rem = divmod(time.time() - start_time, 3600)
            minutes, seconds = divmod(rem, 60)
            print("Program Finished In Time {:0>2}:{:0>2}:{:05.2f}\n".format(int(hours), int(minutes), seconds))


def verify_args(args):
    num_layers = int(args.cache_layers)
    if not os.path.exists(args.trace_file):
        show_error_and_exit("The tracefile: " + str(args.tracefile) + " does not exist!")
    if len(args.cache_sizes) != num_layers:
        show_error_and_exit("Length of --cache-sizes must equal the number of layers: " + str(num_layers))
    if len(args.cache_cycles) != num_layers:
        show_error_and_exit("Length of --cache-cycles must equal the number of layers: " + str(num_layers))
    if len(args.set_associativity) != num_layers:
        show_error_and_exit("Length of --set-associativity must equal the number of layers: " + str(num_layers))
    if args.write_policy != "wb+wa" and args.write_policy != "wt+nwa":
        show_error_and_exit("Write policy must be wb+wa or wt+nwa")
    if args.max_misses < 0:
        show_error_and_exit("--max-misses must be a number greater than or equal to 0!")
    if args.debug_level not in [0,1,2]:
        show_error_and_exit("--debug argument must be 0, 1, or 2!")
    if args.cache_view not in [0,1,2,3]:
        show_error_and_exit("--cache-view argument must be 0, 1, 2, or 3!")



def args_as_list(s):
    v = ast.literal_eval(s)
    if type(v) is not list:
        raise argparse.ArgumentTypeError("Argument \"%s\" is not a list" % (s))
    return v


if __name__ == "__main__":
    # Add our program arguments
    parser = argparse.ArgumentParser(description='Cache Simulator for COE1541 Project 2')
    parser.add_argument('-t', '--tracefile', dest='trace_file', default='', type=str,
                        help='The path to the tracefile for the memory accesses')
    parser.add_argument('-b', '--block-size', dest='block_size', action='store',
                        default=64, type=int,
                        help='Block size in bytes')
    parser.add_argument('-l', '--cache-layers', dest='cache_layers', action='store',
                        default=2, type=int,
                        help='The desired number of layers in the cache')
    parser.add_argument('-s', '--cache-sizes', dest='cache_sizes', action='store',
                        default=[32000, 2000000], type=args_as_list,
                        help='The cache sizes in bytes')
    parser.add_argument('-c', '--cache-cycles', dest='cache_cycles', action='store',
                        default=[1, 50], type=args_as_list,
                        help='Access latency for each layer of the cache')
    parser.add_argument('-a', '--set-associativity', dest='set_associativity', action='store',
                        default=[4, 8], type=args_as_list,
                        help='Set associativity for each cache')
    parser.add_argument('-p', '--write-policy', dest='write_policy', action='store',
                        default='wb+wa', type=str,
                        help='Write/Allocate policy for all levels of cache. Options <wb+wa,wt+nwa>')
    parser.add_argument('-m', '--max-misses', dest='max_misses', action='store',
                        default=0, type=int,
                        help='Maximum number of misses in cache for memory accesses '
                        'to be acknowleged. A value of 0 is sequential access')
    parser.add_argument('-d', '--debug-level', dest='debug_level', action='store',
                        default=1, type=int,
                        help='Verbosity of debug level. 0 = No Output, '
                             '1 = Final Output Tables, 2 = Heirarchy Status at Every Instruction')
    parser.add_argument('-v', '--cache-view', dest='cache_view', action='store',
                        default=2, type=int,
                        help='How to display the contents of each cache. 0 = Stats Only, '
                             '1 = Dirty Sets Only, 2 = Valid Sets Only,3 = All Sets')
    # Parse the arguments
    args = parser.parse_args()

    # Verify they are correct
    verify_args(args)

    # Create memory access sequence
    memory_trace = AccessSequence(args.trace_file)

    # Create cache heirarchy
    cache_heirarchy = create_heirarchy(block_size=args.block_size,
                                       num_layers=args.cache_layers, sizes=args.cache_sizes, cycles=args.cache_cycles,
                                       associativity=args.set_associativity, write_policy=args.write_policy,
                                       max_misses=args.max_misses,cache_view=args.cache_view)

    # Create simulator
    cache_sim = CacheSimulator(memory_trace, cache_heirarchy)

    # Run simulator
    cache_sim.run(args.debug_level)
