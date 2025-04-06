#
# Comet 1 standard library command
# Filename: src\\bin\\sls.py
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

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Lists the contents of the specified directory.", '',
    "USAGE: ls [-h] [-l [-m]] [path ...]", '', "ARGUMENTS", "None",
    "\tLists current working directory", "path",
    "\tDirectory(ies) to list the contents of", '', "OPTIONS",
    "None", "\tList only file/directory names", "-h / --help",
    "\tHelp message", "-l / --long", "\tLong listing format",
    "-m / --modified", "\tUse modified date in long-listing format",
    '', "OUTPUT FORMAT (Long-listing format; | implies absence of a character "
        "at that position)",
    "type|readuser|writeuser|readgrp|writegrp|readother|writeother date "
        "time size name", '', "NOTE", "Item size is in bytes"
)


def longList(path: str, whichDt: str) -> int:
    """
    Long listing.
    Format:
    type|readuser|writeuser|readgrp|writegrp|readother|writeother date time size name
    > param path: Path of directory to be listed
    > param op: Operation next in line to be performed
    > param whichDt: Determine date type to be used (created/modified)
    > return: Error code (0) (ref. src\\errCodes.txt)
    """
    maxSize = 0

    for i in os.scandir(path):
        maxSize = max(maxSize, len(str(i.stat().st_size)))

    for item in os.scandir(path):
        itemData = os.stat(item.path)
        isFl     = os.path.isfile(item)

        print("{} {} {} {}".format(
            yellow + stat.filemode(itemData.st_mode) + reset,
            dt.datetime.fromtimestamp(
                itemData.st_birthtime
                if whichDt == "created" else
                itemData.st_mtime
            ).strftime(r"%d-%m-%Y %H:%M"),
            f"{itemData.st_size if isFl else '-':>{maxSize}}",
            (green if isFl else '') + item.name + reset
        ))

    return 0


def shortList(path: str) -> int:
    """
    Short listing.
    > param path: Path of directory to be listed
    > param lastNl: To print/omit last newline
    > return: Error code (0) (ref. src\\errCodes.txt)
    """
    try:
        maxLen = len(max((i.name for i in os.scandir(path)), key=len))
    except ValueError:
        maxLen = 0

    cnt      = 0
    foundFls = False
    perLine  = os.get_terminal_size().columns // (maxLen + 6)
    if perLine == 0:
        perLine = 1

    for i in os.scandir(path):
        foundFls = True
        isFl     = os.path.isfile(i)
        if cnt % perLine == 0 and cnt:
            cnt = 0
            print()
        if ' ' not in i.name:
            print(f" {green if isFl else ''}"
                  f"{i.name:<{maxLen}}"
                  f"{reset if isFl else ''}",
                  end='  ')
        else:
            print(f"{green if isFl else ''}"
                  f"{'\'' + i.name + '\'':<{maxLen}}"
                  f"{reset if isFl else ''}",
                  end='  ')
        cnt += 1

    print() if foundFls else None
    return 0


def singleLS(path: str, longL: bool, whichDt: str = "created") -> int:
    """
    Single directory listing.
    > param path: Path of the directory to be examined
    > param longL: Do long listing?
    > param whichDt: Determine date type to be used (created/modified)
    > param lastNl: Print/Omit last newline in short listing
    > return: Error code (0, 4) (ref. src\\errCodes.txt)
    """
    err = 0
    if os.path.isdir(path):
        print(pl.Path(path).resolve(), end="\\\n")
        if longL:
            err = longList(path, whichDt)
        else:
            err = shortList(path)
    else:
        return 4
    return err


def LS(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
       args: dict[int, str], opts: dict[int, str], fullComm: str,
       stream: ty.TextIO, op: str) -> int:
    """
    Lists the contents of the specified directory.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Command name
    > param args: Arguments supplied to the command
    > param opts: Options supplied to the command
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0, 2-4) (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'l', 'm', 'h', "-long", "-modified", "-help"}
    fls       = []
    dirs      = []
    flsApp    = fls.append
    dirsApp   = dirs.append
    longL     = False
    modified  = False
    err       = 0

    global green, cyan, reset, bold, yellow
    green     = comm.ANSIGREEN  if op == '' else ''
    cyan      = comm.ANSICYAN   if op == '' else ''
    reset     = comm.ANSIRESET  if op == '' else ''
    bold      = comm.ANSIBOLD   if op == '' else ''
    yellow    = comm.ANSIYELLOW if op == '' else ''

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
            flsApp(arg)
        elif not os.path.exists(arg):
            comm.ERR(f"No such file/directory: \"{arg}\"")
            err = err or 4

    try:
        maxSzFls = len(max((str(os.path.getsize(file)) for file in fls),
                             key=len)) if op == '' else float("inf")
    except ValueError:
        maxSzFls = 0

    flsFinIdx = len(fls) - 1
    dirsFinIdx = len(dirs) - 1

    # Files are processed first...
    for idx, fl in enumerate(fls):
        if not longL:
            print(pl.Path(fl).resolve())
            continue
        itemData = os.stat(fl)
        print("{} {} {} {}".format(
            stat.filemode(itemData.st_mode),
            dt.datetime.fromtimestamp(
                itemData.st_birthtime
            ).strftime(r"%d-%m-%Y %H:%M"),
            f"{itemData.st_size:<{maxSzFls}}",
            pl.Path(fl).resolve()
        ))
        print() if idx == flsFinIdx and dirs else None

    # ... then come the directories
    for idx, dir_ in enumerate(dirs):
        tmp = singleLS(dir_, longL, "modified" if modified else "created")
        err = err or tmp
        print() if idx < dirsFinIdx else None

    return err
