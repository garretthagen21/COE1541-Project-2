import unittest
import os
from memcomponents import heirarchy, access_sequence


def create_test_components(write_policy="wb+wa", trace_file="traces/basic.trace"):
    full_file_path = os.path.join(os.getcwd(), trace_file)
    print(full_file_path)
    test_heirarachy = heirarchy.create_heirarchy(block_size=4,
                                                 num_layers=3, sizes=[256, 512, 1024], cycles=[10, 20, 50],
                                                 associativity=[1, 2, 4], write_policy=write_policy)
    mem_sequence = access_sequence.AccessSequence(full_file_path)
    return (mem_sequence, test_heirarachy)


def is_subset(child_cache, parent_cache):
    parent_blocks = parent_cache.get_valid_blocks()
    child_blocks = child_cache.get_valid_blocks()

    for c_elem in child_blocks:
        if c_elem not in parent_blocks:
            print(str(c_elem)+" not in "+str(parent_blocks))
            return False
    return True


class InclusionTest(unittest.TestCase):

    def test_inclusion_wbwa(self):
        mem_seq, heirarchy = create_test_components()

        for access in mem_seq:
            heirarchy.access(access)
            for cache_num in range(heirarchy.num_layers() - 1):
                subset_result = is_subset(heirarchy.cache_layers[cache_num], heirarchy.cache_layers[cache_num + 1])
                self.assertTrue(subset_result)

    def test_inclusion_wtnwa(self):
        mem_seq, heirarchy = create_test_components("wt+nwa")

        for access in mem_seq:
            heirarchy.access(access)
            for cache_num in range(heirarchy.num_layers() - 1):
                subset_result = is_subset(heirarchy.cache_layers[cache_num], heirarchy.cache_layers[cache_num + 1])
                self.assertTrue(subset_result)


if __name__ == '__main__':
    unittest.main()
