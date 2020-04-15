import csv
import os
import collections
from memcomponents.utilities import *


class Block(object):
    def __init__(self, tag='', valid_bit=False, dirty_bit=False, data="**DATA**"):
        self.tag = tag
        self.valid_bit = valid_bit
        self.dirty_bit = dirty_bit
        self.data = data

    def as_table_entry(self):
        return [self.valid_bit, self.dirty_bit, self.tag, self.data]


def is_hit(block):
    return block is not None and block.valid_bit  # and block.offset == offset


class LRUCache(object):
    def __init__(self, name, block_size_bytes,
                 total_size_bytes, blocks_per_set, latency, wb_wa=True,
                 upper=None,
                 lower=None):
        self.name = name
        self.latency = latency
        self.block_size_bytes = block_size_bytes
        self.blocks_per_set = blocks_per_set
        self.total_size_bytes = total_size_bytes
        self.total_blocks = int(self.total_size_bytes / self.block_size_bytes)
        self.total_sets = int(self.total_blocks / self.blocks_per_set)
        self.wb_wa = wb_wa
        self.lower = lower
        self.upper = upper
        self.num_accesses = 0
        self.num_hits = 0

        self.sets = [LRUSet(self.blocks_per_set) for i in range(self.total_sets)]

    def set_lower(self, cache):
        self.lower = cache

    def set_upper(self, cache):
        self.upper = cache

    def access(self, mem_access):
        # Increment total accesses
        self.num_accesses += 1

        # Add our latency
        mem_access.add_time(self.latency)

        # Parse the address to get our set index
        tag, index, offset = mem_access.parse_address(self.total_sets, self.block_size_bytes)

        # Get the set we are interested in
        found_set = self.sets[index]

        # Attempt to access the block we need, note on hit
        block = found_set.__getitem__(tag)

        # A null block is the equivalent of valid_bit = 0
        if not is_hit(block):

            # Load from lower level on read miss or write miss and
            # write allocate
            if mem_access.mode == 'r' or self.wb_wa:
                # Load from lower level
                block = self.simulate_load(tag, mem_access)

                # Get evicted block if nay
                evicted_block = found_set.__setitem__(tag, block)

                # Activate dirty bit if using write back
                print(evicted_block)
                if self.wb_wa and evicted_block and evicted_block.dirty_bit:
                    print("Simulate write to memomry?")
        # We hit our block
        else:
            self.num_hits += 1

            # It is a write operation and write through policy
            if mem_access.mode == 'w' and not self.wb_wa:
                block.dirty_bit = True

                # So if we are not the bottom layer, continue to propagate down
                if self.lower is not None:
                    self.lower.access(mem_access)
                else:
                    print("Reached main memory write!")

        # Update our sets
        self.sets[index] = found_set

    def simulate_load(self, tag, mem_access):
        # We are the last level so simulate access, by adding 100 to our time
        if self.lower is None:
            if mem_access.mode == 'r':
                mem_access.add_time(self.latency + 100)
        else:
            # Look in the memory source below us
            self.lower.access(mem_access)

        # Create new block to bring into memory
        return Block(tag, True, mem_access.mode == 'w')

    def hit_rate(self):
        return float(self.num_hits) / float(self.num_accesses)

    def miss_rate(self):
        return 1.0 - self.hit_rate()

    # Print out our cache table
    def __repr__(self):
        summary_header = "-- Cache Name: " + str(self.name) + \
                         " -- Latency: " +str(self.latency) + \
                         " -- Cache Size (KB): " + str(self.total_size_bytes / 1000) + \
                         " -- Block Size (B): " + str(self.block_size_bytes) + \
                         " -- Ways: " + str(self.blocks_per_set) + \
                         " -- Hit Rate: " + str(int(self.hit_rate()*100))+"%" + \
                         " -- Miss Rate: " + str(int(self.miss_rate()*100))+"% --\n"
        # Create header
        table_header = ["Index"]
        for i in range(self.blocks_per_set):
            table_header.extend(["V"+str(i),"D"+str(i),"Tag"+str(i),"Data"+str(i)])

        # Create table rows
        table_rows = []
        set_index = 0
        for cache_set in self.sets:
            cache_row = [set_index]
            cache_row += cache_set.as_table_entry()
            table_rows.append(cache_row)
            set_index+=1

        # Create pretty table
        table = PrettyTable(table_header)
        for row in table_rows:
            table.add_row(row)

        # Return our string object
        return summary_header+str(table)






# Base class for paging table
class LRUSet(collections.OrderedDict):

    def __init__(self, maxsize=4, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __getitem__(self, tag):
        value = super().get(tag, None)
        if value is not None:
            self.move_to_end(tag)
        return value

    def __setitem__(self, tag, block):
        super().__setitem__(tag, block)
        evicted = None
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            evicted = self[oldest]
            del self[oldest]

        return evicted

    # Check to see if lookup table is full
    def is_full(self):
        return len(self) > self.maxsize

    def as_table_entry(self):
        block_list = []
        # Fill in actual values
        for block in self.values():
            block_list += block.as_table_entry()
        # Fill remaining space with empty blocks
        for i in range(self.maxsize - len(self)):
            block_list+=Block().as_table_entry()

        return block_list
