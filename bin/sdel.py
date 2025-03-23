#
# Comet 1 standard library command
# Filename: bin\\sdel.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

# Imports
import os
import sys
import shutil as sh
import typing as ty

# Add directory "src\\core" to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Deletes file(s)/directory(ies).", "USAGE: del [-h] [-r] path ...",
    "ARGUMENT(S)", "\tpath", "\t\tPath of file/directory to be deleted",
    "OPTION(S)", "\tNONE", "\t\tNon-recursive delete", "\t-h / --help",
    "\t\tHelp message", "\t-r", "\t\tRecursive delete"
)


def DEL(interpreter: comet.Interpreter, command: str, args: dict[int, str],
        opts: dict[int, str], fullComm: str, stream: ty.TextIO,
        op: str) -> int:
    """
    Deletes a file/directory.
    > param interpreter: Interpreter object
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
                comm.ERR(f"Cannot remove \"{arg}\": use -r option")
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
            comm.ERR("Operation failed: invalid path or file/directory "
                     "in use?")
            return 6

    return 0
