#
# Comet 1 standard library command
# Filename: src\\bin\\sdir.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import datetime as dt
import pathlib  as pl
import typing   as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays the contents one level inside a directory.", '',
    "USAGE: dir [-h] [path ...]", '', "ARGUMENTS",
    "None", "\tLists the current directory", "path",
    "\tDirectory to be listed", '', "OPTIONS", "-h / --help",
    "\tHelp message", '', "OUTPUT FORMAT",
    "create-date create-time modify-date modify-time type size name",
    '', "NOTE", "Sizes are in bytes"
)


def singleDIR(path: str) -> int:
    """
    Print info about the directory given.
    > param path: Path of the directory
    > return: Error code (0, 4-6) (ref. src\\errCodes.txt)
    """
    try:
        maxSz    = 4
        print(path := str(pl.Path(path).resolve()))

        for j in os.scandir(path):
            if len(str(j.stat().st_size)) > maxSz:
                maxSz = len(str(j.stat().st_size))

        for i in os.scandir(path):
            itemInfo = os.stat(i)
            isFl     = os.path.isfile(comm.PTHJN(path, i.name))
            sz       = itemInfo.st_size
            type_    = "FILE" if isFl else "DIR "
            created  = dt.datetime.fromtimestamp(
                itemInfo.st_birthtime
            ).strftime(r'%d-%m-%Y %H:%M:%S')
            modified = dt.datetime.fromtimestamp(
                itemInfo.st_mtime
            ).strftime(r'%d-%m-%Y %H:%M:%S')

            print(f"{created} {modified} {type_} {sz:>{maxSz}} {i.name}")

        return 0
    
    except FileNotFoundError as e:
        comm.ERR(f"Directory modified before dir executed: \"{path}\"", sl=4)
        return 4

    except PermissionError:
        comm.ERR(f"Access is denied to directory: \"{path}\"", sl=4)
        return 5

    except OSError:
        comm.ERR(f"Operation failed; invalid path, directory "
                 f"\"{path}\" in use or unescaped characters?", sl=4)
        return 6


def DIR(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
        args: dict[int, str], opts: dict[int, str], fullComm: str,
        stream: ty.TextIO, op: str) -> int:
    """
    Displays the contents one level inside a directory.
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0, 2, 4-6) (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'h', "-help"}
    argsLen   = len(args)
    err       = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if not args:
        err = singleDIR('.')

    for i, dir_ in enumerate(args.values()):
        if not os.path.isdir(dir_):
            return comm.ERR(f"No such directory: \"{dir_}\"")
        tmp = singleDIR(dir_)
        err = err or tmp
        print() if i != argsLen - 1 else None

    return err
