from pagingalgorithm import *


class LRUAlgorithm(PagingAlgorithm):

    def __init__(self, numFrames, name="LRU"):
        super().__init__(numFrames, name)

    # Public method
    def access(self, address, mode):

        # Attempt to find the page in memory
        pageNode = dictLookup(self.lookupTable, address)

        # Page does not exist so we need to load it
        if pageNode is None:

            # Increment page faults
            self.numPageFaults += 1

            # Create new page entry
            pageNode = PageNode(address)

            # Our page table is full so we need to evict
            if self.isFull():

                # Write to disk if dirty bit is 1
                if self.head.dirtyBit:
                    self.numDiskWrites += 1

                # Evict front node if it exists
                self.remove(self.head)

        # The node already exists so remove it, so we can move it to the back
        else:
            self.remove(pageNode)

        # Regardless we will insert the pageNode to the back
        self.append(pageNode)

        # Only difference between store and load is what we do to the dirty bit
        if mode == "s":
            pageNode.dirtyBit = True

        # Increment accesses
        self.numAccesses += 1
