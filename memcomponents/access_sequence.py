from memcomponents.utilities import *


class MemoryAccess(object):
    def __init__(self, num, mode, address, time):
        self.num = num
        self.mode = mode.lower()
        self.arrival_time = time
        self.serve_time = time
        self.address = address
        self.execution_time = 0

    def parse_address(self, num_sets, block_size, addr_size=32, debug=False):
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
            print("Binary Address: " + str(bin_string))
            print("Tag: " + bin_string[0:num_bits_tag])
            print("Index: " + bin_string[num_bits_tag:-num_bits_offset])
            print("Offset: " + bin_string[-num_bits_offset:])

        # Return split address
        return (tag, index, offset)

    def set_serve_time(self, serve_time):
        self.serve_time = max(serve_time, self.arrival_time)

    def add_time(self, time):
        self.execution_time += time

    def finish_time(self):
        return self.serve_time + self.execution_time

    def wait_time(self):
        return self.serve_time - self.arrival_time

    def is_write(self):
        return self.mode == 'r'

    def as_table_entry(self):
        return [self.num, self.mode, self.address, self.arrival_time, self.serve_time, self.finish_time(),
                self.execution_time]

    def __repr__(self):
        return "Instruction: " + str(self.num) + " | Mode: " + self.mode + " | Address: " + str(
            self.address) + " | Arrival Time: " + str(
            self.arrival_time) + " | Serve Time: " + str(self.serve_time) + " | Return Time: " + str(
            self.finish_time()) + " | Access Time: " + str(self.execution_time)


class AccessSequence(object):

    def __init__(self, trace_file):
        # Initialize our trace sequence
        self.mem_sequence = []
        self.curr_index = 0

        # Read in our traces
        t_file = open(trace_file, 'r')
        line_num = 0
        for line in t_file.readlines():
            tokens = line.split()
            mem_access = MemoryAccess(line_num, tokens[0], int(tokens[1]), int(tokens[2]))
            self.mem_sequence.append(mem_access)
            line_num += 1
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
        table = PrettyTable(
            ["Instruction Num", "Mode", "Address", "Arrival Time", "Serve Time", "Finish Time", "Access Time"])
        seq_str = "--- Memory Access Summary ---\n"
        for mem_access in self.mem_sequence:
            table.add_row(mem_access.as_table_entry())

        return seq_str + str(table)
