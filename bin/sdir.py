#
# Comet 1 standard library command
# Filename: bin\\sdir.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import datetime as dt
import pathlib  as pl
import typing   as ty

# Add directory "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays the contents one level inside a directory.",
    "USAGE: dir [-h] [path ...]", "OUTPUT FORMAT",
    "<date-created> <time-created> <date-modified> <time-modified> <type> "
        "<size> <name>", "ARGUMENT(S)",
    "\tNONE", "\t\tLists the current directory", "\tpath",
    "\t\tDirectory to be listed", "OPTION(S)", "\t-h / --help",
    "\t\tHelp message"
)


def singleDIR(path: str) -> int:
    """
    Print info about the directory given.
    > param path: Path of the directory
    > return: Error code (0, 4-6) (ref. src\\errCodes.txt)
    """
    try:
        path    = str(pl.Path(path).resolve())
        maxSize = 4
        print('"' + path + '"')

        for j in os.scandir(path):
            if len(str(j.stat().st_size)) > maxSize:
                maxSize = len(str(j.stat().st_size))

        for i in os.scandir(path):
            isFl     = os.path.isfile(comm.PTHJN(path, i.name))
            created  = dt.datetime.fromtimestamp(
                os.path.getctime(comm.PTHJN(path, i.name))
            )
            modified = dt.datetime.fromtimestamp(
                os.path.getmtime(comm.PTHJN(path, i.name))
            )

            print("{ctime} {mtime} {type_} {size:>{maxSize}} {name}".format(
                ctime=created.strftime(r'%d-%m-%Y %H:%M:%S'),
                mtime=modified.strftime(r'%d-%m-%Y %H:%M:%S'),
                type_='FILE' if isFl else 'DIR ',
                size=(os.path.getsize(comm.PTHJN(path, i.name))
                        if isFl else '-'),
                maxSize=maxSize,
                name=i.name
                ))

        return 0
    
    except FileNotFoundError as e:
        comm.ERR(f"Directory modified before dir executed: \"{path}\"", sl=4)
        return 4

    except PermissionError:
        comm.ERR(f"Access is denied to directory: \"{path}\"", sl=4)
        return 5

    except OSError:
        comm.ERR(f"Operation failed; invalid path or directory "
                 f"\"{path}\" in use?", sl=4)
        return 6


def DIR(interpreter: comet.Interpreter, command: str, args: dict[int, str],
        opts: dict[int, str], fullComm: str, stream: ty.TextIO,
        op: str) -> int:
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
    optVals   = comm.lowerLT(opts.values())
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
