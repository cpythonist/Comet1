#
# Comet 1 standard library command
# Filename: src\\bin\\stouch.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import pathlib as pl
import typing  as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Creates (\"touches\") a new file.", '', "USAGE: touch [-h] file ...", '',
    "ARGUMENTS", "file", "\tFilename for the new file", '',
    "OPTIONS", "-h / --help", "\tHelp message"
)


def TOUCH(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
          args: dict[int, str], opts: dict[int, str], fullComm: str,
          stream: ty.TextIO, op: str) -> int:
    """
    Wait a certain amount of time before continuing.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Command name
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2, 5, 6, 8) (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
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

    for path in args.values():
        if os.path.isfile(path):
            comm.ERR(f"File exists: {pl.Path(path).resolve()}")
            err = err or 8
            continue
        elif os.path.isdir(path):
            comm.ERR(f"Directory exists: {pl.Path(path).resolve()}")
            err = err or 8
            continue

        try:
            open(path, 'w').close()
        except PermissionError:
            comm.ERR(f"Access is denied to touch: {pl.Path(path).resolve()}")
            err = err or 5
        except OSError:
            comm.ERR("Operation failed; invalid filename, disc full or "
                     "unescaped characters?")
            err = err or 6

    return err
