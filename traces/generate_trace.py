import argparse
import random




def convert_to_base(decimal_number, base,addr_size):
    DIGITS = '0123456789abcdef'
    remainder_stack = []

    while decimal_number > 0:
        remainder = decimal_number % base
        remainder_stack.append(remainder)
        decimal_number = decimal_number // base

    new_digits = []
    while remainder_stack:
        new_digits.append(DIGITS[remainder_stack.pop()])

    # Hack to make binary numbers addr_size bits
    if base == 2:
        while len(new_digits) < addr_size:
            new_digits.insert(0,'0')


    return ''.join(new_digits)
def coin_flip(prob=0.5):
    prob = min(1.0, max(0.0, prob))
    return random.randint(1, 100) <= prob * 100


def create_trace_file(filename, addr_size, num_accesses, reuse_rate,number_base):
    wFile = open(filename, 'w+')
    maxAddr = 2 ** addr_size - 1
    time = 0
    used_addr = []
    for i in range(num_accesses):
        # Generate a new address
        if i == 0 or not coin_flip(reuse_rate):
            new_addr = random.randint(0, maxAddr)
            used_addr.append(new_addr)
        # Reuse address
        else:
            new_addr = used_addr[random.randint(0, len(used_addr) - 1)]

        # Get the access mode
        mode = 'w' if coin_flip() else 'r'

        # Convert to appropriate number system
        new_addr = convert_to_base(new_addr,number_base,addr_size)

        # Write to the file
        wFile.write(str(mode)+" "+str(new_addr)+" "+str(time)+"\n")

        # Increment our time
        time += random.randint(0, 4)

    wFile.close()


if __name__ == "__main__":
    # Add our program arguments
    parser = argparse.ArgumentParser(description='Create a trace file for testing cache accesses')
    parser.add_argument('-f', '--filename', dest='file_name', default='default.trace', type=str,
                        help="Filename for output tracefile")
    parser.add_argument('-s', '--addr-size', dest='addr_size', default=32, type=int, help="Address size in bits")
    parser.add_argument('-a', '--num-accesses', dest='num_accesses', default=100, type=int,
                        help="How many accesses we want")
    parser.add_argument('-b', '--base',dest='number_base',default=10,type=int,help="Number base (e.g. decimal = 10, binary = 2, hex = 16)")
    parser.add_argument('-r', '--reuse-rate', dest='reuse_rate', default=0.3, type=float,
                        help="How often we want to reuse an existing address, This will increase hit rate")

    # Parse the arguments
    args = parser.parse_args()

    # Verify they are correct
    create_trace_file(args.file_name, args.addr_size, args.num_accesses, args.reuse_rate,args.number_base)

    print("Done!")
