#
# Comet 1 standard library command
# Filename: bin\\sls.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import stat
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
    "Lists the contents of the specified directory.",
    "USAGE: ls [-h] [-l [-m]] [path ...]", "ARGUMENT(S)", "\tNONE",
    "\t\tLists current working directory", "\tpath",
    "\t\tDirectory(ies) to list the contents of", "OPTION(S)",
    "\tNONE", "\t\tList only file/directory names", "\t-h / --help",
    "\t\tHelp message", "\t-l / --long", "\t\tLong listing format",
    "\t-m / --modified", "\t\tUse modified date"
)


def longList(path: str, whichDt: str) -> int:
    """
    Long listing.
    Format:
    <type><readowner><writeowner><readgroup><writegroup><readother><writeother> <date> <time> <size> <name>
    > param path: Path of directory to be listed
    > param whichDt: Determine date type to be used (created/modified)
    > return: Error code (0) (ref. src\\errCodes.txt)
    """
    maxSize = 0

    for i in os.scandir(path):
        maxSize = max(maxSize, len(str(i.stat().st_size)))

    for item in os.scandir(path):
        itemData = os.stat(item.path)
        isFile   = os.path.isfile(item)
        print("{} {} {} {}".format(
            stat.filemode(itemData.st_mode),
            dt.datetime.fromtimestamp(
                itemData.st_birthtime
                if whichDt == "created" else
                itemData.st_mtime
            ).strftime(r"%d-%m-%Y %H:%M"),
            f"{itemData.st_size if isFile else '-':>{maxSize}}",
            item.name
        ))

    return 0


def shortList(path: str) -> int:
    """
    Short listing.
    > param path: Path of directory to be listed
    > return: Error code (0) (ref. src\\errCodes.txt)
    """
    try:
        maxLen = len(max((i.name for i in os.scandir(path)), key=len))
    except ValueError:
        maxLen = 0

    cnt     = 0
    perLine = os.get_terminal_size().columns // (maxLen + 6)
    if perLine == 0:
        perLine = 1

    for i in os.scandir(path):
        if cnt % perLine == 0 and cnt:
            cnt = 0
            print()
        if ' ' not in i.name:
            print(f" {i.name:<{maxLen}}", end='  ')
        else:
            print(f"{'"' + i.name + '"':<{maxLen}} ", end='  ')
        cnt += 1

    print()
    return 0


def singleLS(path: str, longL: bool, whichDt: str = "created") -> int:
    """
    Single directory listing.
    > param path: Path of the directory to be examined
    > param longL: Do long listing?
    > param whichDt: Determine date type to be used (created/modified)
    > return: Error code (0, 4) (ref. src\\errCodes.txt)
    """
    err = 0
    if os.path.isdir(path):
        print('"' + str(pl.Path(path).resolve()) + '"')
        if longL:
            err = longList(path, whichDt)
        else:
            err = shortList(path)
    else:
        return 4
    return err


def LS(interpreter: comet.Interpreter, command: str, args: dict[int, str],
       opts: dict[int, str], fullComm: str, stream: ty.TextIO,
       op: str) -> int:
    """
    Lists the contents of the specified directory.
    > param interpreter: Interpreter object
    > param command: Command name
    > param args: Arguments supplied to the command
    > param opts: Options supplied to the command
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0, 2-4) (ref. src\\errCodes.txt)
    """
    optVals   = comm.lowerLT(opts.values())
    validOpts = {'l', 'm', 'h',
                 "-long", "-modified", "-help"}
    files     = []
    dirs      = []
    filesApp  = files.append
    dirsApp   = dirs.append
    longL     = False
    modified  = False
    argsLen   = len(args)
    err       = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt == 'l' or opt == "-long":
                longL = True
            elif opt == 'm' or opt == "-modified":
                modified = True
        if 'm' in optVals and 'l' not in optVals:
            comm.ERR("Option -m must be used with -l")
            return 3

    if not args:
        err = singleLS('.', longL, "modified" if modified else "created")
        if isinstance(err, tuple):
            err = err[0]

    for arg in args.values():
        if os.path.isdir(arg):
            dirsApp(arg)
        elif os.path.isfile(arg):
            filesApp(arg)
        elif not os.path.exists(arg):
            comm.ERR(f"No such file/directory: \"{arg}\"")
            err = err or 4

    try:
        maxSizeFls = len(max((str(os.path.getsize(file)) for file in files),
                             key=len))
    except ValueError:
        maxSizeFls = 0

    flsLen = len(files)
    for idx, file in enumerate(files):
        if not longL:
            print('"' + str(pl.Path(file).resolve()) + '"')
            continue
        itemData = os.stat(file)
        print("{} {} {} {}".format(
            stat.filemode(itemData.st_mode),
            dt.datetime.fromtimestamp(
                itemData.st_birthtime
            ).strftime(r"%d-%m-%Y %H:%M"),
            f"{itemData.st_size:<{maxSizeFls}}",
            pl.Path(file).resolve()
        ))
        print() if idx != flsLen - 1 else None

    dirsLen = len(dirs)
    for idx, item in enumerate(dirs):
        tmp = singleLS(item, longL, "modified" if modified else "created")
        err = err or tmp
        print() if idx != dirsLen - 1 else None

    return err
