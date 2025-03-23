#
# Comet 1 standard library command
# Filename: bin\\sfile.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import mimetypes as mt
import pathlib   as pl
import typing    as ty

# Add directory "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays the type of a path (file or directory).",
    "USAGE: file [-h] [-r[0 | 1 | 2 | 3]] path [...]", "ARGUMENT(S)",
    "\tpath", "\t\tPaths to be examined", "OPTION(S)", "\t-h / --help",
    "\t\tHelp message", "\t-r[0 | 1 | 2 | 3]",
    "\t\t'Human-readable' memory values", "\t\t0 - bytes",
    "\t\t1 - kilobytes (1000 B)", "\t\t2 - megabytes (1000 kB)",
    "\t\t3 - gigabytes (1000 MB)"
)


def _HELPER_FILE(givenFileOrDir: str, num: int) -> int:
    """
    Helper function of the FILE function. For printing item information of a
    single item.
    > param givenFileOrDir: Path to be examined
    > param num: 'Human-readable' memory values (10 ** x)
    > return: Error code (0, 4-6) (ref. src\\errCodes.txt)
    """
    try:
        # Get type of file
        type_ = mt.guess_type(givenFileOrDir)

        if os.path.isfile(givenFileOrDir):
            size  = os.path.getsize(givenFileOrDir)
            alpha = ''
            if num == 4:
                if len(str(size)) >= 9:
                    size  /= 1000000000
                    alpha  = 'G'
                elif len(str(size)) >= 6:
                    size  /= 1000000
                    alpha  = 'M'
                elif len(str(size)) >= 3:
                    size  /= 1000
                    alpha  = 'k'
            else:
                alpha = ('', 'k', 'M', 'G')[num]
                size  /= 1000 ** num

            print("\"{}\"\n{} {} {}{}B".format(
                pl.Path(givenFileOrDir).resolve(),
                type_[0] if type_[0] is not None else "unknown",
                type_[1] if type_[1] is not None else '-',
                size,
                alpha
            ))

        elif os.path.isdir(givenFileOrDir):
            print(f"\"{pl.Path(givenFileOrDir).resolve()}\"\ndirectory - -")

        else:
            # Will be caught in the except block
            raise FileNotFoundError

        return 0

    except FileNotFoundError:
        comm.ERR(f"No such file/directory: \"{givenFileOrDir}\"", sl=4)
        return 4

    except PermissionError:
        comm.ERR(f"Access is denied: \"{givenFileOrDir}\"", sl=4)
        return 5

    except OSError:
        comm.ERR(f"Operation failed; invalid name or file/directory in use?",
                 sl=4)
        return 6


def FILE(interpreter: comet.Interpreter, command: str, args: dict[int, str],
         opts: dict[int, str], fullComm: str, stream: ty.TextIO,
         op: str) -> int:
    """
    Displays the type of a path (file or directory).
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-6) (ref. src\\errCodes.txt)
    """
    optVals      = comm.lowerLT(opts.values())
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
                    comm.ERR("Multiple format options given")
                    return 3
                num          = int(rem if (rem := opt[1:]) != '' else 4)
                formatChosen = True

    if not args:
        comm.ERR("Incorrect format")
        return 1

    for arg in args.values():
        tmp = _HELPER_FILE(arg, num)
        err = err or tmp

    return err
