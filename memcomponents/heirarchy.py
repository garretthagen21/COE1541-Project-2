from memcomponents.cache import LRUCache
from memcomponents.utilities import *

class CacheHeirarchy(object):
    def __init__(self,outstanding_misses=0):
        self.last_access = None
        self.miss_limit = outstanding_misses
        self.cache_layers = []

    def is_sequential(self):
        return self.miss_limit == 0

    def add_cache(self, new_cache):
        prev_cache = self.cache_layers[-1] if self.cache_layers else None
        if prev_cache:
            prev_cache.set_lower(new_cache)

        new_cache.set_upper(prev_cache)
        self.cache_layers.append(new_cache)

    def access(self, mem_access):
        if self.num_layers() > 0:

            # If the cache is sequential, we should not start our next access
            # until 1 cycle after the previous access has returned
            if self.is_sequential() and self.last_access:
                mem_access.set_serve_time(self.last_access.finish_time()+1)
            else:
                pass #TODO: implement access under miss logic

            self.cache_layers[0].access(mem_access)
            self.last_access = mem_access
        else:
            print("Cache Heirarachy Empty!")

    def num_layers(self):
        return len(self.cache_layers)

    def __repr__(self):
        heirarchy_str="<<<<<<<<<<< Heirarchy Snapshot >>>>>>>>>>>\n\n"

        for cache in self.cache_layers:
            heirarchy_str+=str(cache)
            heirarchy_str+='\n'+draw_vertical_line(5,15)+'\n'

        heirarchy_str+=" ==================== MAIN MEMORY =================== "

        return heirarchy_str








def create_heirarchy(block_size, num_layers, sizes, cycles, associativity, write_policy,max_misses=0):
    # Init heirarchy
    heirarchy = CacheHeirarchy(max_misses)

    # Create the new cache
    for i in range(num_layers):
        new_cache = LRUCache(name="L" + str(i),
                             block_size_bytes=block_size,
                             total_size_bytes=adjust_to_standard_size(sizes[i]),
                             blocks_per_set=associativity[i],
                             latency=cycles[i],
                             wb_wa=(write_policy == "wb+wa"))
        heirarchy.add_cache(new_cache)
    return heirarchy
