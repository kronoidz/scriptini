#!/usr/bin/env python3

# printbin
# Print the binary representation of a decimal number using two's complement
# for negative numbers

from argparse import ArgumentParser
from sys import stderr


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Print the binary representation of a decimal number."
    )
    parser.add_argument("number", metavar="N", type=int,
        help="The number to convert"
    )
    parser.add_argument("--bits", "-b", metavar="B", type=int,
        help="The number of bits to use in the conversion "
            "(required if N is negative)"
    )
    args = parser.parse_args()

    if args.bits is not None and args.bits < 0:
        print("Invalid bit number: {}".format(args.bits), file=stderr)
        exit(1)
    
    if args.number < 0 and args.bits is None:
        print("Use --bits for negative numbers", file=stderr)
        exit(1)
    
    if args.bits is None:
        print(format(args.number, "b"))
    else:
        if args.bits == 0:
            exit()
        
        for i in reversed(range(args.bits)):
            print((args.number >> i) & 1, end="")
        
        print()
