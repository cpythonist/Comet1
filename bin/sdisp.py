#
# Comet 1 standard library command
# Filename: bin\\sdisplay.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

# Imports
import os
import sys
import pathlib as pl
import typing  as ty

# Add directory "src\\core" to list variable sys.path
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)) + os.sep + "core")
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays the contents of a text file.",
    "USAGE: display [-h] [-i] file ...", "ARGUMENT(S)", "\tfile",
    "\t\tFile to be displayed", "OPTION(S)", "\tNONE",
    "\t\tDoes not display file information", "\t-h / --help",
    "\t\tHelp message", "\t-i / --info", "\t\tDisplay file information"
)


def _DISP_HELPER(path: str, info: bool) -> int:
    """
    Helper function of DISP, displays a single file.
    > param path: Path of the file to be displayed
    > param info: Determine whether file information is to be printed
    > return: Error code (0, 4-6) (ref. src\\errCodes.txt)
    """
    try:
        with open(path, 'r', buffering=1) as f:
            print('"' + str(pl.Path(path).resolve()) + '"')
            print(f"Size: {os.path.getsize(path)} B") if info else None
            for line in f:
                print(line, end='')
        print()
        return 0
    except FileNotFoundError:
        comm.ERR(f"No such file: \"{path}\"", sl=4)
        return 4
    except PermissionError:
        comm.ERR(f"Access is denied: \"{path}\"", sl=4)
        return 5
    except OSError:
        comm.ERR("Operation failed; invalid path or file in use?", sl=4)
        return 6



def DISP(interpreter: comet.Interpreter, command: str, args: dict[int, str],
         opts: dict[int, str], fullComm: str, stream: ty.TextIO,
         op: str) -> int:
    """
    Displays the contents of a text file.
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2, 4-6) (ref. src\\errCodes.txt)
    """
    optVals   = comm.lowerLT(opts.values())
    validOpts = {'i', 'h', "-info", "-help"}
    info      = False
    err       = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt == 'i' or opt == "-info":
                info = True

    if not args:
        comm.ERR("Incorrect format")
        return 1

    for arg in args.values():
        if not os.path.isfile(arg):
            comm.ERR(f"No such file: \"{arg}\"")
            err = err or 4
            continue
        tmp = _DISP_HELPER(arg, info)
        err = err or tmp

    return err
