import unittest
import os
from memcomponents import heirarchy, access_sequence


def create_test_components(write_policy="wb+wa", trace_file="traces/basic.trace"):
    full_file_path = os.path.join(os.getcwd(), trace_file)
    test_heirarachy = heirarchy.create_heirarchy(block_size=4,
                                                 num_layers=3, sizes=[256, 512, 1024], cycles=[10, 20, 50],
                                                 associativity=[1, 2, 4], write_policy=write_policy)
    mem_sequence = access_sequence.AccessSequence(full_file_path)
    return (mem_sequence, test_heirarachy)


def make_block_pool(cache_sets):
    valid_blocks = []
    for cache_set in cache_sets:
        valid_blocks.extend(cache_set.get_valid_blocks())


def is_subset(child_cache, parent_cache):
    parent_blocks = make_block_pool(parent_cache.get_valid_sets())
    child_blocks = make_block_pool(child_cache.get_valid_sets())

    for c_elem in child_blocks:
        if c_elem not in parent_blocks:
            print(str(c_elem) + " not in " + str(parent_blocks))
            return False
    return True


class InclusionTest(unittest.TestCase):

    def test_inclusion_wbwa(self):
        mem_seq, c_heirarchy = create_test_components()

        for access in mem_seq:
            c_heirarchy.access(access)
            for cache_num in range(c_heirarchy.num_layers() - 1):
                subset_result = is_subset(c_heirarchy.cache_layers[cache_num], c_heirarchy.cache_layers[cache_num + 1])
                self.assertTrue(subset_result)

    def test_inclusion_wtnwa(self):
        mem_seq, c_heirarchy = create_test_components("wt+nwa")

        for access in mem_seq:
            c_heirarchy.access(access)
            for cache_num in range(c_heirarchy.num_layers() - 1):
                subset_result = is_subset(c_heirarchy.cache_layers[cache_num], c_heirarchy.cache_layers[cache_num + 1])
                self.assertTrue(subset_result)


if __name__ == '__main__':
    unittest.main()
