#
# Comet 1 standard library command
# Filename: src\\bin\\sdisp.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import pathlib as pl
import typing  as ty

# Add src\\core to sys.path
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)) + os.sep + "core")
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays the contents of a text file.",
    "USAGE: display [-h] [-i] file ...", '', "ARGUMENTS", "file",
    "\tFile to be displayed", '', "OPTIONS", "None",
    "\tDoes not display file information", "-h / --help", "\tHelp message",
    "-i / --info", "\tDisplay file information", '', "OUTPUT FORMAT",
    "\"filename\"", "size (if -i option is used)", "file-contents",
    '', "NOTE", "File size is in bytes"
)


def DISP(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
         args: dict[int, str], opts: dict[int, str], fullComm: str,
         stream: ty.TextIO, op: str) -> int:
    """
    Displays the contents of a text file.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2, 4-6) (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'i', 'h', "-info", "-help"}
    info      = False

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

    if args == {} or len(args) >= 2:
        comm.ERR("Incorrect format")
        return 1

    arg = args[sorted(args)[0]]
    if not os.path.isfile(arg):
        comm.ERR(f"No such file: \"{arg}\"")
        return 4

    try:
        with open(arg, 'r', buffering=1) as f:
            # This ln1 stupidity is done to avoid printing the file name in
            # case of a UnicodeDecodeError, which is raised only when we try
            # to iterate through the lines of the file
            ln1 = f.__next__()
            print('"' + str(pl.Path(arg).resolve()) + '"')
            print(f"Size: {os.path.getsize(arg)} B") if info else None
            print(ln1, end='')
            for line in f:
                print(line, end='')
        print()
        return 0

    except FileNotFoundError:
        comm.ERR(f"No such file: \"{arg}\"", sl=4)
        return 4

    except PermissionError:
        comm.ERR(f"Access is denied: \"{arg}\"", sl=4)
        return 5

    except OSError:
        comm.ERR("Operation failed; invalid path, file in use or unescaped "
                 "characters?", sl=4)
        return 6

    except UnicodeDecodeError:
        comm.ERR("Does not appear to contain text", sl=4)
        return 9
