from memcomponents.utilities import *


class MemoryAccess(object):
    def __init__(self, mode, address, time):
        self.mode = mode
        self.start_time = time
        self.address = address
        self.execution_time = 0

    def parse_address(self, num_sets, block_size, addr_size=32,debug=False):
        num_bits_index = bits_required(num_sets)
        num_bits_offset = bits_required(block_size)
        num_bits_tag = addr_size - (num_bits_index + num_bits_offset)


        bin_string = '{:032b}'.format(self.address)

        # Tag is num_bits_tag MSB
        tag = int(bin_string[0:num_bits_tag], 2)
        index = int(bin_string[num_bits_tag:-num_bits_offset], 2)
        offset = int(bin_string[-num_bits_offset:], 2)

        # If we need to debug
        if debug:
            print(self)
            print("Sets: " + str(num_sets))
            print("Block Size: " + str(block_size))
            print("Num Bits Index: " + str(num_bits_index))
            print("Num Bits Tag: " + str(num_bits_tag))
            print("Num Bits Offset: " + str(num_bits_offset))
            print()
            print("Binary Address: "+str(bin_string))
            print("Tag: " + bin_string[0:num_bits_tag])
            print("Index: " + bin_string[num_bits_tag:-num_bits_offset])
            print("Offset: " + bin_string[-num_bits_offset:])

        # Return split address
        return (tag, index, offset)

    def add_time(self, time):
        self.execution_time += time

    def finish_time(self):
        return self.start_time + self.execution_time

    def is_write(self):
        return self.mode == 'r'

    def as_table_entry(self):
        return [self.mode, self.address, self.start_time, self.finish_time()]

    def __repr__(self):
        return self.mode + " " + str(self.address) + " " + str(self.start_time) + str(self.finish_time())


class AccessSequence(object):

    def __init__(self, trace_file, sequential=False):
        # Initialize our trace sequence
        self.mem_sequence = []
        self.curr_index = 0

        # Read in our traces
        t_file = open(trace_file, 'r')
        for line in t_file.readlines():
            tokens = line.split()
            mem_access = MemoryAccess(tokens[0], int(tokens[1]), int(tokens[2]))
            self.mem_sequence.append(mem_access)
        t_file.close()

    def __iter__(self):
        self.curr_index = 0
        return self

    def __next__(self):
        if self.curr_index < len(self.mem_sequence):
            mem_access = self.mem_sequence[self.curr_index]
            self.curr_index += 1
            return mem_access
        else:
            raise StopIteration

    def __repr__(self):
        table = PrettyTable(["Instruction Num","Mode","Address","Start Time","End Time"])
        line_num = 0
        seq_str = "--- Memory Access Summary ---\n"
        for mem_access in self.mem_sequence:
            table.add_row([line_num]+mem_access.as_table_entry())
            line_num+=1


        return seq_str+str(table)
