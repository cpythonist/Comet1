#
# Comet 1 standard library command
# Filename: bin\\smd.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import pathlib as pl
import typing  as ty

srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Creates a new directory.", "USAGE: MD [-h] name ...", "ARGUMENT(S)",
    "\tname", "\t\tName(s) of the new directory(ies)", "OPTION(S)",
    "\t-h / --help", "\t\tHelp message"
)


def MD(interpreter: comet.Interpreter, command: str, args: dict[int, str],
       opts: dict[int, str], fullComm: str, stream: ty.TextIO,
       op: str) -> int:
    """
    Creates a new directory.
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2) (ref. src\\errCodes.txt)
    """
    optVals   = comm.lowerLT(opts.values())
    validOpts = {'h', "-help"}
    err       = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if not args:
        comm.ERR("Incorrect format")
        return 1

    for arg in args.values():
        try:
            os.makedirs(arg)
        except FileExistsError:
            if os.path.isdir(arg):
                comm.ERR("Directory already exists: "
                         f"\"{pl.Path(arg).resolve()}\"")
            else:
                comm.ERR(f"File already exists: \"{pl.Path(arg).resolve()}\"")
            err = err or 8
        except OSError:
            comm.ERR(f"Operation failed; invalid path or disc full? \"{arg}\"")
            err = err or 6

    return err
