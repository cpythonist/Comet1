#
# Comet 1 standard library command
# Filename: src\\bin\\scp.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as sh
import typing as ty

# Add src\\core to sys.path temporarily
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Copies a file/directory to another directory.", '',
    "USAGE: CP [-h] [-r] src dest", '', "ARGUMENTS", "src",
    "\tPath of source file/directory", "dest",
    "\tDestination for copying source", '', "OPTIONS", "None",
    "\tNon-recursive copy (?)", "-h / --help", "\tHelp message",
    "-r / --recurse", "\tRecursive copy"
)


def cpSrcToDest(src: str, dest: str) -> int:
    """
    > param src: Path of source file/directory
    > param dest: Destination for copying source
    > return: Error code (0, 4) (ref src\\errCodes.txt)
    """
    if not os.path.isdir(dest):
        comm.ERR(f"No such directory: \"{dest}\"", sl=4)
        return 4
    if os.path.isfile(src):
        sh.copyfile(src, dest)
    elif os.path.isdir(src):
        sh.copytree(src, dest, dirs_exist_ok=True)
    else:
        comm.ERR(f"No such file/directory: \"{src}\"", sl=4)
        return 4
    return 0


def CP(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
       args: dict[int, str], opts: dict[int, str], fullComm: str,
       stream: ty.TextIO, op: str) -> int:
    """
    Copies a file/directory to another directory.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2, 4-7) (ref. src\\errCodes.txt)
    """
    argsSorted = sorted(args)
    optVals    = comm.LOWERLT(opts.values())
    validOpts  = {'h', "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if len(args) != 2:
        comm.ERR(f"Incorrect format")
        return 1

    try:
        src = args[argsSorted[0]]
        dst = args[argsSorted[1]]
        err = cpSrcToDest(src, dst)
        return err

    except FileNotFoundError:
        comm.ERR("Race condition: Source or destination modified before "
                 "cp executed")
        return 7

    except PermissionError:
        comm.ERR("Access is denied")
        return 5

    except OSError:
        comm.ERR("Operation failed; invalid path, access is denied, "
                 "the file/directory in use or unescaped characters?")
        return 6
