#
# Comet 1 standard library command
# Filename: src\\bin\\swhoami.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import typing  as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = ("Displays the currently logged in user.", '', "USAGE: whoami [-h]",
           '', "OPTIONS", "-h / --help", "\tHelp message")


def WHOAMI(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
           args: dict[int, str], opts: dict[int, str], fullComm: str,
           stream: ty.TextIO, op: str) -> int:
    """
    Checks for the existance of a path.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2) (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'h', "-help"}
    
    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if args:
        comm.ERR("Incorrect format")
        return 1
    
    print(os.getlogin())
    return 0
