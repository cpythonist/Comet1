#
# Comet 1 standard library command
# Filename: bin\\secho.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import typing as ty

# Add directory "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Echoes a string.", "USAGE: echo [-h] [-s sepStr] [str ...]",
    "ARGUMENT(S)", "\tNONE", "\t\tEchoes an empty line", "\tstr",
    "\t\tString(s) to be echoed", "\tsepStr",
    "\t\tSeparation string; must follow '-s / --sep' option", "OPTION(S)",
    "\t-h / --help", "\t\tHelp message", "\t-s", "\t\tDefine separation string"
)


def ECHO(interpreter: comet.Interpreter, command: str, args: dict[int, str],
         opts: dict[int, str], fullComm: str, stream: ty.TextIO,
         op: str) -> int:
    """
    Echoes a string or writes a string to a file.
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0, 2, 3) (ref. src\\errCodes.txt)
    """
    sep       = ' '
    optVals   = comm.lowerLT(opts.values())
    validOpts = {'s', 'h', "-sep", "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

        sOptGiven = False, ''
        for opt in opts.keys():
            if opts[opt].lower() == 's' or opts[opt].lower() == "-sep":
                if sOptGiven[0]:
                    comm.ERR(f"-{sOptGiven[1]} was already given")
                    return 3
                try:
                    sep = args[opt + 1]
                    args.pop(opt + 1)
                except KeyError:
                    comm.ERR(f"-{opts[opt]} must be followed by separation "
                             "string")
                    return 3
                sOptGiven = True, opts[opt]

    print(*(args.values()), sep=sep)
    return 0
