from memcomponents.cache import LRUCache
from memcomponents.utilities import *


class CacheHeirarchy(object):
    def __init__(self, outstanding_misses=0):
        self.last_access = None
        self.miss_limit = outstanding_misses
        self.cache_layers = []
        self.access_buffer = []

    def invalidate(self):
        self.access_buffer = []
        self.last_access = None
        for cache_layer in self.cache_layers:
            cache_layer.invalidate()

    def add_cache(self, new_cache):
        prev_cache = self.cache_layers[-1] if self.cache_layers else None
        if prev_cache:
            prev_cache.set_lower(new_cache)

        new_cache.set_upper(prev_cache)
        self.cache_layers.append(new_cache)

    def access(self, mem_access):

        if self.num_layers() > 0:
            # Adjust the serve time of the access
            mem_access = self.adjust_serve_time(mem_access)

            # Perform the access. Note this will set the finish time
            self.cache_layers[0].access(mem_access)

            # Add the access to our buffer
            self.access_buffer.append(mem_access)
        else:
            show_error_and_exit("Cache Heirarchy Is Empty! Cannot perform " + str(mem_access))

    def adjust_serve_time(self, mem_access):

        min_finish_access = None
        for pending_access in self.access_buffer:

            # If an instruction has completed before this access, remove it
            if pending_access.finish_time() < mem_access.arrival_time:
                self.access_buffer.remove(pending_access)

            # Calculate our minimum access in case we need it
            elif not min_finish_access or pending_access.finish_time() < min_finish_access.finish_time():
                min_finish_access = pending_access

        # If our buffer is at max capacity we need to simulate the minimum access finishing by
        # starting our current access at the minimum pending access's finish time + 1
        if self.access_buffer and min_finish_access and \
                len(self.access_buffer) >= self.miss_limit:
            # The new access should start one second after the pending access
            # that is scheduled to finish first in the buffer
            mem_access.set_serve_time(min_finish_access.finish_time() + 1)

            # Remove the pending access from the buffer
            self.access_buffer.remove(min_finish_access)

        return mem_access

    def num_layers(self):
        return len(self.cache_layers)

    def __repr__(self):
        heirarchy_str = "<<<<<<<<<<< Heirarchy Snapshot >>>>>>>>>>>\n\n"

        for cache in self.cache_layers:
            heirarchy_str += str(cache)
            heirarchy_str += '\n' + draw_vertical_line(5, 15) + '\n'

        heirarchy_str += " ==================== MAIN MEMORY =================== "

        return heirarchy_str


def create_heirarchy(block_size, num_layers, sizes, cycles, associativity, write_policy, max_misses,cache_view=2):
    # Init heirarchy
    heirarchy = CacheHeirarchy(max_misses)

    # Create the new cache
    for i in range(num_layers):
        new_cache = LRUCache(name="L" + str(i),
                             block_size_bytes=block_size,
                             total_size_bytes=adjust_to_standard_size(sizes[i]),
                             blocks_per_set=associativity[i],
                             latency=cycles[i],
                             wb_wa=(write_policy == "wb+wa"),
                             debug=cache_view)
        heirarchy.add_cache(new_cache)
    return heirarchy
