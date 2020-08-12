#!/usr/bin/env python3

# Memorize a .csv file of pairs

import re
import random

from argparse import ArgumentParser
from pathlib import Path
from sys import stderr

game_description = """
mem is a game that helps you memorize large sets of key-value pairs.
It reads a 2-column CSV file and asks the player to associate each key
(first column by default, second column with the flip flag on) to a value.
It keeps asking until the player guesses all values.
"""

def main():
    parser = ArgumentParser(description=game_description)
    parser.add_argument("--list", "-l", action="store_true", help="list available memfiles")
    parser.add_argument("--flip", "-f", action="store_true", help="flip couples in memfile")
    parser.add_argument("memfile", type=str, help="stem of memfile to use", nargs="?", default="")
    args = parser.parse_args()
    
    # Get path
    mempath = Path.home() / "MEGA" / "mem"
    if not mempath.is_dir():
        raise NotADirectoryError("{mempath} is not a directory or does not exist")
    
    # --list
    if args.list:
        print("\n".join(f.stem for f in list(mempath.glob("*.csv"))))
        exit(0)
    
    if not args.memfile:
        print("Invalid argument usage. Use -h for help.", file=stderr)
        exit(1)
    
    filepath = mempath / (args.memfile + ".csv")
    if not filepath.is_file():
        raise FileNotFoundError("{filepath} is not a file or does not exist")

    # Read the file into a list
    with open(filepath) as myfile:
        data = myfile.readlines()

    # Validate all lines in file
    pattern = re.compile("^.+,.+\n?$")
    for d in data:
        if not pattern.match(d):
            print("Invalid file line: {0}".format(d), file=sys.stderr)
            exit(1)

    # Deserialize data in dictionary
    dic = {}
    for line in data:
        s = line.replace("\n", "").split(",")
        if args.flip:
            key = s[1]
            value = s[0]
        else:
            key = s[0]
            value = s[1]
        if not key in dic:
            dic[key] = []
        dic[key].append(value)

    # Main loop
    while len(dic) > 0:

        print()

        # Get random value
        randindex = random.randint(0, len(dic) - 1)
        randkey = list(dic.keys())[randindex]
        values = list(dic[randkey])

        correct = True

        while len(values) > 0:
            hint = randkey

            if len(values) > 1:
                hint += " (" + str(len(values)) + " remaining) > "
            else:
                hint += " > "

            # Acquire input
            guess = input(hint)

            guessed = False
            for value in values:
                if guess.lower() == value.lower():
                    guessed = True
                    values.remove(value)
                    break
            
            if not guessed:
                print("WRONG! " + str(dic[randkey]))
                correct = False
                break

        if correct:
            del dic[randkey]


    print("\nEND: YOU WIN\n")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPROGRAM INTERRUPTED: YOU LOOSE\n")
        exit(0)
