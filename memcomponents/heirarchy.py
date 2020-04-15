from memcomponents.cache import LRUCache
from memcomponents.utilities import *

class CacheHeirarchy(object):
    def __init__(self):
        self.cache_layers = []

    def add_cache(self, new_cache):
        prev_cache = self.cache_layers[-1] if self.cache_layers else None
        if prev_cache:
            prev_cache.set_lower(new_cache)

        new_cache.set_upper(prev_cache)
        self.cache_layers.append(new_cache)

    def access(self, mem_access):
        if self.num_layers() > 0:
            self.cache_layers[0].access(mem_access)
        else:
            print("Cache heirarachy empty!")

    def num_layers(self):
        return len(self.cache_layers)

    def __repr__(self):
        heirarchy_str=""

        for cache in self.cache_layers:
            heirarchy_str+=str(cache)
            heirarchy_str+='\n'+draw_vertical_line(5,15)+'\n'

        heirarchy_str+=" ==================== MAIN MEMORY =================== "

        return heirarchy_str








def create_heirarchy(block_size, num_layers, sizes, cycles, associativity, write_policy):
    heirarchy = CacheHeirarchy()

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
