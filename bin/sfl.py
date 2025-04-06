#
# Comet 1 standard library command
# Filename: src\\bin\\sfl.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import mimetypes as mt
import pathlib   as pl
import typing    as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays the type of a path (file or directory).", '',
    "USAGE: fl [-h] [-r[1 | 2 | 3]] path [...]", '', "ARGUMENTS",
    "path", "\tPath to be examined", '', "OPTIONS", "-h / --help",
    "\tHelp message", "-r[1 | 2 | 3]",
    "\t'Human-readable' memory values", "\tNone - best unit",
    "\t1 - kilobytes (1000 B)", "\t2 - megabytes (1000 kB)",
    "\t3 - gigabytes (1000 MB)"
)


def _HELPER_FL(givenFlOrDir: str, num: int) -> tuple[tuple[str, str, str], int]:
    """
    Helper function of the FL function. For printing item information of a
    single item.
    > param givenFlOrDir: Path to be examined
    > param num: 'Human-readable' memory values (10 ** x)
    > return: Error code (0, 4-6) (ref. src\\errCodes.txt)
    """
    try:
        # Get type of file
        toReturn: list[tuple[str, str, str]]
        type_    = mt.guess_type(givenFlOrDir)
        toReturn = []

        if os.path.isfile(givenFlOrDir):
            size  = os.path.getsize(givenFlOrDir)
            alpha = ''
            if num == 4:
                szLen = len(str(size))
                if szLen > 9:
                    size  /= 1000000000
                    alpha  = 'G'
                elif szLen > 6:
                    size  /= 1000000
                    alpha  = 'M'
                elif szLen > 3:
                    size  /= 1000
                    alpha  = 'k'
            else:
                alpha = ('', 'k', 'M', 'G')[num]
                size  /= 1000 ** num

            return (str(pl.Path(givenFlOrDir).resolve()),
                    (type_[0] if type_[0] is not None else "unknown"),
                    str(round(size, 3)) + f"{alpha}B"), 0

        elif os.path.isdir(givenFlOrDir):
            return (str(pl.Path(givenFlOrDir).resolve()),
                    "directory", '-'), 0

        else:
            # Will be caught in the except block
            raise FileNotFoundError

    except FileNotFoundError:
        comm.ERR(f"No such file/directory: \"{givenFlOrDir}\"", sl=4)
        return tuple(), 4

    except PermissionError:
        comm.ERR(f"Access is denied: \"{givenFlOrDir}\"", sl=4)
        return tuple(), 5

    except OSError:
        comm.ERR(f"Operation failed; invalid name, file/directory in use or "
                 "unescaped characters?", sl=4)
        return tuple(), 6


def FL(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
       args: dict[int, str], opts: dict[int, str], fullComm: str,
       stream: ty.TextIO, op: str) -> int:
    """
    Displays the type of a path (file or directory).
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-6) (ref. src\\errCodes.txt)
    """
    optVals      = comm.LOWERLT(opts.values())
    validOpts    = {'r', "r1", "r2", "r3", 'h', "-help"}
    formatChosen = False
    num          = 0
    err          = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt[0] == 'r':
                if formatChosen:
                    comm.ERR("Cannot accept multiple format options")
                    return 3
                num          = int(rem if (rem := opt[1:]) != '' else 4)
                formatChosen = True

    if not args:
        comm.ERR("Incorrect format")
        return 1

    for arg in args.values():
        tmp = _HELPER_FL(arg, num)
        if tmp[1] != 0:
            err = err or tmp[1]
            continue
        print(f"{tmp[0][0]}\n{tmp[0][1]} {tmp[0][2]}")

    return err
