#
# Comet 1 standard library command
# Filename: src\\bin\\sclip.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import subprocess as sp
import typing     as ty

# Add directory "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Copies strings to the clipboard.", '', "USAGE: clip [-h] [-s sep] str ...",
    '', "ARGUMENTS", "str", "\tString to be copied", '', "OPTIONS",
    "-h / --help", "\tHelp message", "-s", "\tDefine separation string"
)


def CLIP(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
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
    > return: Error code (0-3) (ref. src\\errCodes.txt)
    """
    optVals         = comm.LOWERLT(opts.values())
    validOpts       = {'h', 's',
                       "-sep", "-help"}
    sep             = ' '
    err             = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for pos in opts:
            opt = opts[pos].lower()
            if opt == 's' or opt == "-sep":
                if pos + 1 not in args:
                    comm.ERR(f"One argument must follow -{opt}")
                    return 3
                sep = args[pos + 1]
                args.pop(pos + 1)

    if not args:
        comm.ERR("Incorrect format")
        return 1

    output = sp.run(["clip.exe"], input=sep.join(args.values()),
                    check=True, text=True)
    return err
