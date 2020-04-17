import csv
import os
import collections
from memcomponents.utilities import *


class Block(object):
    def __init__(self, tag='', valid_bit=False, dirty_bit=False, data=""):
        self.tag = tag
        self.valid_bit = valid_bit
        self.dirty_bit = dirty_bit
        self.data = data

    def as_table_entry(self):
        return [self.valid_bit, self.dirty_bit, self.tag, self.data]

    def __eq__(self, obj):
        return isinstance(obj, Block) and \
               obj.data == self.data and \
               obj.valid_bit == self.valid_bit

    def __repr__(self):
        return "Block --" \
               " Tag: " + str(self.tag) + \
               " Valid: " + str(self.valid_bit) + \
               " Dirty: " + str(self.dirty_bit) + \
               " Data: " + str(self.data)


def is_hit(block):
    return block is not None and block.valid_bit  # and block.offset == offset


class LRUCache(object):
    def __init__(self, name, block_size_bytes,
                 total_size_bytes, blocks_per_set, latency, wb_wa=True,
                 upper=None,
                 lower=None,
                 debug=2):
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
        self.debug = debug
        self.sets = [LRUSet(set_index,self.blocks_per_set) for set_index in range(self.total_sets)]

    def set_lower(self, cache):
        self.lower = cache

    def set_upper(self, cache):
        self.upper = cache

    def get_valid_sets(self, dirty_required=False):
        valid_sets = []
        for cache_set in self.sets:
            valid_blocks = cache_set.get_valid_blocks(dirty_required)
            if valid_blocks:
                valid_sets.append(cache_set)
        return valid_sets

    def invalidate(self):
        self.num_accesses = 0
        self.num_hits = 0
        self.sets = [LRUSet(self.blocks_per_set) for i in range(self.total_sets)]

    def access(self, mem_access):

        # Increment total accesses
        self.num_accesses += 1

        # Add our latency
        mem_access.add_time(self.latency)

        # Parse the address to get our set index
        tag, index, offset = mem_access.parse_address(self.total_sets, self.block_size_bytes)

        # Get the set we are interested in
        found_set = self.sets[index]

        # Attempt to access the block we need, note on hit it will be moved to the front
        block = found_set.__getitem__(tag)

        # A null block is the equivalent of valid_bit = 0
        if not is_hit(block):

            # Load from lower level on read miss or write miss and
            # write allocate. If we miss on wt_nwa write, we do nothing
            if mem_access.mode == 'r' or self.wb_wa:
                # Simulate load for cache miss
                block = self.simulate_load_from(tag, mem_access)

                # Get evicted block if any
                evicted_block = found_set.__setitem__(tag, block)

                # Write straight to memory if using write back #TODO: do we need to account for latency here?
                if self.wb_wa and evicted_block and evicted_block.dirty_bit:
                    mem_access.add_time(self.get_memory_latency())

            # Write miss for write through - we still need to check other levels
            else:
                self.simulate_store_to(mem_access)

        # We hit our block
        else:
            self.num_hits += 1

            # It is a write operation and write through policy
            if mem_access.mode == 'w':
                block.dirty_bit = True

                # If doing write through we need to write diry at all layers
                if not self.wb_wa:
                    self.simulate_store_to(mem_access)

        # Update our sets
        self.sets[index] = found_set

    def simulate_store_to(self, mem_access):
        # If we are not the bottom layer, continue to propagate down
        if self.lower:
            self.lower.access(mem_access)
        # If write-through and we have reached the bottom, write to memory
        else:
            mem_access.add_time(self.latency + 100)

    def simulate_load_from(self, tag, mem_access):
        # We are the last level so simulate access, by adding 100 to our time
        if self.lower:
            # Look in the memory source below us
            self.lower.access(mem_access)
        else:
            # if mem_access.mode == 'r': #TODO: This adds latency for wa
            mem_access.add_time(self.latency + 100)

        # Create new block to bring into memory, simulating from the
        return Block(tag, True, mem_access.mode == 'w', mem_access.address)

    def get_memory_latency(self):
        # Find the last level of cache
        level = self
        while level.lower:
            level = level.lower

        # Return the last level + 100
        return level.latency + 100

    def hit_rate(self):
        try:
            return float(self.num_hits) / float(self.num_accesses)
        except ZeroDivisionError:
            return 0.0

    def miss_rate(self):
        return 1.0 - self.hit_rate()

    def stat_string(self):
        return " *** Cache: " + str(self.name) + " ***\n" \
               " -- Latency: " + str(self.latency) + \
               " -- Cache Size (KB): " + str(self.total_size_bytes / 1000) + \
               " -- Block Size (B): " + str(self.block_size_bytes) + \
               " -- Ways: " + str(self.blocks_per_set) + "\n" \
               " -- Accesses: " + str(self.num_accesses) + \
               " -- Hits: " + str(self.num_hits) + \
               " -- Misses: " + str(self.num_accesses - self.num_hits) + \
               " -- Hit Rate: " + str(int(self.hit_rate() * 100)) + "%" + \
               " -- Miss Rate: " + str(int(self.miss_rate() * 100)) + "%\n"

    # Print out our cache table
    def __repr__(self):

        # Determine what we want to show based on our debug arams
        if self.debug == 3:
            table_sets = self.sets
        elif self.debug == 2:
            table_sets = self.get_valid_sets(False)
        elif self.debug == 1:
            table_sets = self.get_valid_sets(True)
        else:
            return self.stat_string()


        # Create header
        table_header = ["Index"]
        for i in range(self.blocks_per_set):
            table_header.extend(["V" + str(i), "D" + str(i), "Tag" + str(i), "Data" + str(i)])



        # Create table rows
        table_rows = []
        for cache_set in table_sets:
            table_rows.append(cache_set.as_table_entry())

        # Create pretty table
        table = PrettyTable(table_header)
        for row in table_rows:
            table.add_row(row)

        # Return our string object
        return self.stat_string() + str(table)


# Base class for paging table
class LRUSet(collections.OrderedDict):

    def __init__(self,index=0, maxsize=4, *args, **kwds):
        self.index = index
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
        if self.is_full():
            oldest = next(iter(self))
            evicted = self[oldest]
            del self[oldest]

        return evicted

    # Check to see if lookup table is full
    def is_full(self):
        return len(self) > self.maxsize

    def get_valid_blocks(self, dirty_required=False):
        valid_blocks = []

        for block in self.values():
            condition = block.valid_bit
            if dirty_required:
                condition = condition and block.dirty_bit
            if condition:
                valid_blocks.append(block)

        return valid_blocks

    def as_table_entry(self):
        block_list = [self.index]

        # Fill in actual values
        for block in self.values():
            block_list += block.as_table_entry()

        # Fill remaining space with empty blocks
        for i in range(self.maxsize - len(self)):
            block_list += Block().as_table_entry()

        return block_list
