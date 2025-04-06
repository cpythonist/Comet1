#
# Comet 1 standard library command
# Filename: src\\bin\\sispath.py
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
    "Checks for the existance of a path.", '',
    "USAGE: ispath [-h] [-f | -d] [-e] path ...", '', "ARGUMENTS", "path",
    "\tPath of file to be checked", '', "OPTIONS", "None",
    "\tChecks for existance of a file/directory with given name",
    "-d", "\tChecks for the existance of a directory with given name",
    "-e", "\tEnsures that the path exists", "-f",
    "\tChecks for the existance of a file with given name",
    "-h / --help", "\tHelp message"
)


def ISPATH(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
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
    > return: Error code (0-4) (ref. src\\errCodes.txt)
    """
    optVals         = comm.LOWERLT(opts.values())
    validOpts       = {'f', 'd', 'e', 'h',
                       "-file", "-directory", "-exists", "-help"}
    optAlreadyGiven = False
    func            = os.path.exists
    mustExist       = False
    err             = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt not in ('f', 'd', "-file", "-directory"):
                continue
            if optAlreadyGiven:
                comm.ERR("Check option already given")
                return 3
            if opt == 'f' or opt == "-file":
                func = os.path.isfile
            elif opt == 'd' or opt == "-directory":
                func = os.path.isdir
            optAlreadyGiven = True
        # -e option
        mustExist = True if 'e' in optVals else False

    if not args:
        comm.ERR("Incorrect format")
        return 1

    for arg in args.values():
        res = func(arg)
        if mustExist and not os.path.exists(arg):
            comm.ERR(f"Does not exist: \"{arg}\"")
            err = err or 4
        else:
            print('"' + str(pl.Path(arg).resolve()) + '"', res)

    return err
