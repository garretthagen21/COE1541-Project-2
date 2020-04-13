#!/usr/bin/env python3

import time
import argparse
import sys
from lru import LRUAlgorithm
from optimal import OptimalAlgorithm
from secondchance import SecondChanceAlgorithm
from pagingalgorithm import parseAddressString



def showErrorAndExit(errorReason,errorCode = 1):
    print("[Error] "+errorReason+" Exiting program...\n")
    sys.exit(errorCode)


class MemoryAccess(object):
    def __init__(self,mode,rawAddr,lineNum):
        self.mode = mode
        self.lineNum = lineNum
        addrTuple = parseAddressString(rawAddr)
        self.address = addrTuple[0]
        self.offset = addrTuple[1]



class VirtualSimulator(object):
    def __init__(self, traceFile, numFrames, algorithmType,outputFile):

        # For csv
        self.outputFile = outputFile

        # Initialize our trace sequence
        self.memorySequence = []
        tFile = open(traceFile, 'r')
        lineNum = 0
        for line in tFile.readlines():
            lineTokens = line.split()
            memoryAccess = MemoryAccess(lineTokens[0],lineTokens[1],lineNum)
            self.memorySequence.append(memoryAccess)
            lineNum+=1
        tFile.close()

        # Create paging algorithm
        if algorithmType == "opt":
            self.pagingAlgorithm = OptimalAlgorithm(numFrames)
            self.pagingAlgorithm.setInstructions(self.memorySequence)
        elif algorithmType == "lru":
            self.pagingAlgorithm = LRUAlgorithm(numFrames)
        elif algorithmType == "second":
            self.pagingAlgorithm = SecondChanceAlgorithm(numFrames)
        else:
            showErrorAndExit("Invalid algorithm: "+algorithmType)



    def run(self,debug = 0):
        # Record execution time
        startTime = time.time()

        # Execute the memory trace
        for memAccess in self.memorySequence:
            self.pagingAlgorithm.access(memAccess.address, memAccess.mode)
            if debug > 1:
                self.pagingAlgorithm.printSummary()

        # Print our summary
        self.pagingAlgorithm.printSummary()



        if debug > 0:
            # Write our csv so we can print graphs
            self.pagingAlgorithm.writeCSV(self.outputFile)

            # Write our execution time
            hours, rem = divmod(time.time() - startTime, 3600)
            minutes, seconds = divmod(rem, 60)
            print("Program Finished In Time {:0>2}:{:0>2}:{:05.2f}\n".format(int(hours), int(minutes), seconds))




if __name__ == "__main__":

    # Add our program arguments
    parser = argparse.ArgumentParser(description='Virtual memory manager for CS1550')
    parser.add_argument('tracefile', nargs='?', default='', type=str,
                        help='The path to the tracefile for the memory accesses')
    parser.add_argument('-n', '--numframes', dest='num_frames', action='store',
                        default=10, type=int,
                        help='The desired number of frames simulate')
    parser.add_argument('-a', '--algorithm', dest='algorithm', action='store',
                        default='opt', type=str,
                        help='The type of algorithm to run. Options: <opt|lru|second>')
    parser.add_argument('-c', '--csvfile', dest='csvfile', action='store',
                        default='output.csv', type=str,
                        help='Where to write/append the statistic results')
    parser.add_argument('-d', '--debug', dest='debug', action='store',
                        default=0, type=int,
                        help='Where to write/append the statistic results')

    # Parse the arguments
    args = parser.parse_args()

    # Create and run simulator
    virtualSim = VirtualSimulator(args.tracefile, int(args.num_frames), args.algorithm, args.csvfile)
    virtualSim.run(args.debug)
