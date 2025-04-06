# 
# Clash 1 standard library command
# Filename: bin\sfind.py
# Copyright (c) 2024, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
# 

# Imports
import os
import re
import sys
import typing as ty

# Add directory "src\\core" to list variable sys.path
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = """
Searches for a substrings using regular expressions in a given string.
Syntax:
    FIND regex string [-c]
Arguments:
    regex: Regular expression for matching substrings
    string: String to be searched in
Option:
    -c: Case-sensitive search
"""

def FIND(varTable: dict[str, str], origPth: str, prevErr: int, command: str, args: dict[int, str],
         opts: dict[int, str], fullComm: str, stream: ty.TextIO) -> int:
    """
    Searches for a substring in a string given.
    """
    try:
        caseIn = True
        if opts:
            if len(opts) != 1:
                return comm.error(f"Too many options: {comm.optsJoin(opts)}",
                                  func=command)
            if comm.LOWERLT(opts)[0] != 'c':
                return comm.error(f"Unknown option: {comm.optsJoin(opts)}",
                                  func=command)
            caseIn = False
        
        if len(args) != 2:
            return comm.error("Incorrect format", func=command)
        
        regex, string = args.values()
        string        = string if caseIn else string.lower()
        pattern       = re.compile(regex)
        skip          = 0
        while True:
            match = pattern.search(string)
            if not match:
                break
            print(f"{match.start() + 1 + skip}", end='')
            # Cut the string, to eliminate the already searched part.
            string  = string[match.start()+1:]
            skip   += match.start()
            if string:
                print(' ', end='')
            else:
                print()

        # temp      = string.find(substring)
        # while temp != -1:
        #     # Positions for humans is one greater than indices used by Python.
        #     print(f"{temp + 1}", end='')
        #     # Cut the string, to eliminate the already searched part.
        #     string = string[temp + len(substring):]
        #     temp = string.find(substring)
        #     # More matches are found.
        #     if temp != -1:
        #         print(' ', end='')
        #     # No more matches are found.
        #     else:
        #         print()
        
        return 0
    
    # Never observed
    except Exception as e:
        return comm.reportUnknownErr(e, func=command)
