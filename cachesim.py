#!/usr/bin/env python3

import ast
import time
import argparse
import os
import sys
from memcomponents import cache
from memcomponents.utilities import *
from memcomponents.access_sequence import AccessSequence
from memcomponents.heirarchy import *



class CacheSimulator(object):
    def __init__(self, sequence, heirarchy):
        self.sequence = sequence
        self.heirarchy = heirarchy

    def run(self, debug=1):
        # Record execution time
        startTime = time.time()

        # Execute the memory trace
        for mem_access in self.sequence:
            self.heirarchy.access(mem_access)

        if debug > 0:
            print("\n"+str(self.sequence)+"\n")
            print("\n"+str(self.heirarchy)+"\n")

            # Write our execution time
            hours, rem = divmod(time.time() - startTime, 3600)
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
    if args.version != "sequential" and args.version != "access-under-misses":
        show_error_and_exit("Version must be sequential or access-under-misses")


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
                        default=10, type=int,
                        help='Maximum number of misses for memory accesses to be acknowleged')
    parser.add_argument('-v', '--version', dest='version', action='store',
                        default='sequential', type=str,
                        help='Write/Allocate policy for all levels of cache. Options <sequential,access-under-misses>')

    # Parse the arguments
    args = parser.parse_args()

    # Verify they are correct
    verify_args(args)

    # Create memory access sequence
    memory_trace = AccessSequence(args.trace_file)

    # Create cache heirarchy
    cache_heirarchy = create_heirarchy(block_size=args.block_size,
                                       num_layers=args.cache_layers, sizes=args.cache_sizes, cycles=args.cache_cycles,
                                       associativity=args.set_associativity, write_policy=args.write_policy)

    # Create simulator
    cache_sim = CacheSimulator(memory_trace, cache_heirarchy)
    cache_sim.run()
