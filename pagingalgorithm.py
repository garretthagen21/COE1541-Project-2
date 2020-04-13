import csv
import os

# Page node that will be used in page replacement algorithm
class PageNode(object):
    def __init__(self, address, refBit = False ,dirtyBit = False, prev=None, next=None):
        self.address = address
        self.refBit = refBit
        self.dirtyBit = dirtyBit
        self.prev = prev
        self.next = next


# Base class for paging table
class PagingAlgorithm(object):

    def __init__(self, numFrames,name = "DEFAULT"):
        self.algoName = name
        self.numFrames = numFrames
        self.numDiskWrites = 0
        self.numPageFaults = 0
        self.numAccesses = 0
        self.head = None
        self.tail = None
        self.lookupTable = {}

    # Remove page node from lookup table
    def remove(self, pageNode):

        # Connect prev pointer to next pointer
        if pageNode.prev:
            pageNode.prev.next = pageNode.next

        # Connect next pointer to prev pointer
        if pageNode.next:
            pageNode.next.prev = pageNode.prev

        # If this was the head move it
        if pageNode is self.head:
            self.head = pageNode.next

        # If this was the tail move it
        if pageNode is self.tail:
            self.tail = pageNode.prev

        # Remove entry from hashmap
        del self.lookupTable[pageNode.address]

        # private method to append page node

    # Append page node to end of list
    def append(self, pageNode):

        # Append to end
        currTail = self.tail
        pageNode.prev = currTail
        if currTail:
            currTail.next = pageNode

        # New tail is page node
        self.tail = pageNode
        self.tail.next = None

        # If this is also the first node we need to set the head
        if not self.head:
            self.head = self.tail

        # Add entry to hashmap lookuptable
        self.lookupTable[pageNode.address] = pageNode

    # Check to see if lookup table is full
    def isFull(self):
        return len(self.lookupTable) >= self.numFrames

    # Mainly for debugging
    def displayPageTable(self):
        currNode = self.head
        print("["+self.algoName+"]  Access Num: " + str(self.numAccesses))
        print("\tLinked List: ")
        for i in range(self.numFrames):
            if currNode:
                currNode = currNode.next
                print("\t| " + str(i) + " | " + str(currNode.address) + " | " + str(currNode.dirtyBit) + " |")
            else:
                print("\t| " + str(i) + " | XXXXXXX | X |")

        print("\tLookup Table:")
        i = 0
        for key, value in self.lookupTable.items():
            print("\t| " + str(i) + " -> " + str(key) + " | " + str(value.dirtyBit) + " |")
            i += 1

        print("\n")



    def printSummary(self):
        print("Algorithm: "+str(self.algoName))
        print("Number of frames: "+str(self.numFrames))
        print("Total memory accesses: "+str(self.numAccesses))
        print("Total page faults: "+str(self.numPageFaults))
        print("Total writes to disk: "+str(self.numDiskWrites))

    def writeCSV(self,csvFile):

        # Figure out our index
        if self.algoName == "LRU":
            ourIndex = 1
        elif self.algoName == "SECOND":
            ourIndex = 2
        else:
            ourIndex = 3

        csvRows = []
        # Try and load existing csv information
        if os.path.exists(csvFile):
            rFile = open(csvFile,'r')
            reader = csv.reader(rFile)
            for row in reader:
                csvRows.append(row)
            rFile.close()
        else:
            csvRows = [["Frames","LRU","SECOND","OPT"]]



        foundRow = False
        for row in csvRows:
            # Transfer other measurements if we already have an entry
            if row[0] == str(self.numFrames):
                row[ourIndex] = str(self.numPageFaults)
                foundRow = True

        # if we need to make a new row
        if not foundRow:
            newRow = [str(self.numFrames), "0", "0", "0"]
            newRow[ourIndex] = str(self.numPageFaults)
            csvRows.append(newRow)

        wFile = open(csvFile, 'w')
        csvWriter = csv.writer(wFile)
        csvWriter.writerows(csvRows)
        wFile.close()




    # Pythonic pure virtual functions
    def access(self, address, mode):
        raise NotImplementedError("Error: access() not implemented")



# Get the address and offset of the address string in decimal
def parseAddressString(rawAddress):
    hexData = rawAddress.split('x')[1]
    addrPortion = hexData[0:-3]
    offsetPortion = rawAddress[-3:]
    return addrPortion,offsetPortion

 # Convenience dict lookup
def dictLookup(dict,key):
    try:
        return dict[key]
    except KeyError:
        return None
