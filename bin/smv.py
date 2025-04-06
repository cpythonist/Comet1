#
# Comet 1 standard library command
# Filename: src\\bin\\smv.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as sh
import typing as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Moves a file or directory.", '', "USAGE: mv [-h] src dest", '',
    "ARGUMENTS", "src", "\tSource file/directory", "dest",
    "\tDestination file/directory", '', "OPTIONS", "-h / --help",
    "\tDisplay help message"
)


def MV(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
       args: dict[int, str], opts: dict[int, str], fullComm: str,
       stream: ty.TextIO, op: str) -> int:
    """
    Moves a file or directory.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Command name
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2, 4, 5) (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'h', "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in opts or "-help" in opts:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if len(args) != 2:
        comm.ERR("Incorrect format")
        return 1

    src = args[sorted(args)[0]]
    dst = args[sorted(args)[1]]
    try:
        sh.move(src, dst)
    except FileNotFoundError:
        comm.ERR(f"No such file/directory: \"{src}\"")
        return 4
    except PermissionError:
        comm.ERR("Access is denied")
        return 5
    return 0
