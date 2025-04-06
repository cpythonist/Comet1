#
# Comet 1 standard library command
# Filename: src\\bin\\srm.py
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
    "Removes files and directories.", '', "USAGE: rm [-h] [-r] path ...", '',
    "ARGUMENTS", "path", "\tPath of file/directory to be removed", '',
    "OPTIONS", "None", "\tNon-recursive delete", "-h / --help",
    "\tHelp message", "-r", "\tRecursive delete"
)


def RM(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
       args: dict[int, str], opts: dict[int, str], fullComm: str,
       stream: ty.TextIO, op: str) -> int:
    """
    Removes a file/directory.
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
    recurse   = False
    optVals   = opts.values()
    validOpts = {'r', 'h', "-recurse", "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt in ('r', "-recurse"):
                recurse = True

    if not args:
        comm.ERR("Incorrect format")
        return 1

    for idx in sorted(args):
        arg = args[idx]

        try:
            if os.path.isfile(arg):
                os.remove(arg)
            elif os.path.isdir(arg) and recurse:
                sh.rmtree(arg)
            elif os.path.isdir(arg) and not recurse:
                comm.ERR(f"Cannot remove \"{arg}\": Is a directory; use -r "
                         "option")
                return 3
            else:
                comm.ERR(f"No such file/directory: \"{arg}\"")
                return 4

        except PermissionError:
            comm.ERR(f"Access is denied: \"{arg}\"")
            return 5

        except FileNotFoundError:
            comm.ERR(f"No such file/directory: \"{arg}\"")
            return 4

        except OSError:
            comm.ERR("Operation failed: invalid path, file/directory in use "
                     "or unescaped characters?")
            return 6

    return 0
