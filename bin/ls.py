#
# Comet 1 standard library command
# Filename: src\\bin\\ls.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import math
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

helpStr = b"x\x9ceQ\xcbn\xc20\x10<g\xbfb\x8fpH\xb8\xb7\'\xa4R\x8a\x14\x12\x04\xc9\xa9\xe2`\x92Mb\xd5\x8f\xc86B\xa9\xf8\xf8\xda\xa6\xb4\x15=d\xb4;\xde\x99}$\xe7\xd6Yt\x03a\xa3\x95#\xe5\x13\xdd\xc5\xdc\x8e\xd4\xf0\x8eS\x8b-7\xd48m\xa6\x0c\xa0>,\xd7\xab\'\x14\x16\xdf\xd3\xe1\xe8A\xf8O\x1e}427`\x96eG\x80\xe5~]oWEu\x80B+\x82$\x8fM\x9a\xb31\xbe\x01^\xb4\xf9\xe0\xaa\xff\xb5\x85 \x85\xe4\xe5\x9e\xcf8\xd99:\x8d\xc2\xeb\x1eg\x03(w\xd5\xa6,\xfez\xa3Vb\xc2\x8e\x0bZ\xfc\x98\xa2b\x92,\xa4\x03.0M\x07\x12#$o\x1e\xd1\xb3\x96\xf5\x04~\xf2\xf0\"\xb4\xea\xbd\x8b\xc7\xd8.\x0c\xd6i#\x99\x83T\xc6\x02\xa9\xdbx\x06HjKx\xcf\xb0e\x8e\x90+\x0c\xfa\xf4A\te]\xed\xea\n_\xcb\xfdvY\xe1,\xff_\xf3\x8cW\xe4r\x14~Ud\'K\xaa\xa1px\x86\xcd\xc0\x0ck\x1c\x19daw\x0f\xa3\xb6\xdcq\xad\xe6\xe0\xa6\x91\xae\x86X{\xb6d\xae\x17\xc3\x1d\xc5(P\xbd\x19oL\x08\x02\xa1\xfd\xe1\xbe\x8bbx\x9b\xd8q\xe9\x7f-\xff\xa4x\x1f\x80\xa2\xacV\xb0q$o$\xb7a\xa7\xd3\xe4\xc8~\x01\xb1u\xba\t"


def _longList_HELPER_LS(path: str, green: str, yellow: str, reset: str,
                        whichDt: str) -> tuple[str, int]:
    """
    Long listing.
    Format:
    type|readuser|writeuser|readgrp|writegrp|readother|writeother date time size name
    > param path: Path of directory to be listed
    > param op: Operation next in line to be performed
    > param debug: Is debugging enabled?
    > param green: ANSI code for green
    > param yellow: ANSI code for yellow
    > param reset: ANSI code for reset
    > param whichDt: Determine date type to be used (created/modified)
    > return: String to be printed and error code (ref. src\\errCodes.txt)
    """
    toRet: list[str]
    items: list[tuple[str, bool, str, os.stat_result]]
    maxSz    = 0
    toRet    = []
    items    = []
    itemsApp = items.append
    toRetApp = toRet.append

    try:
        with os.scandir(path) as iter_:
            entries = [entry for entry in iter_]
    except PermissionError:
        return '', comm.ERR_PERMDENIED
    except FileNotFoundError:
        return '', comm.ERR_RACECONDN

    for entry in entries:
        try:
            itemData = entry.stat()
            isFl     = entry.is_file()
            szStr    = str(itemData.st_size) if isFl else '-'
            maxSz    = max(maxSz, len(szStr))
            itemsApp((entry.name, isFl, szStr, itemData))
        except FileNotFoundError:
            continue

    toRetApp(f"total {str(len(items))}")

    for nm, isFl, sz, data in items:
        itemMode = yellow + stat.filemode(data.st_mode) + reset
        date     = dt.datetime.fromtimestamp(
            data.st_birthtime if whichDt == "created" else data.st_mtime
        ).strftime(r"%d-%m-%Y %H:%M")
        itemSz   = f"{sz if isFl else '-':>{maxSz}}"
        itemNm   = (green if isFl else '') + nm + (reset if isFl else '')

        toRetApp(f"{itemMode} {date} {itemSz} {itemNm}")

    return '\n'.join(toRet), comm.ERR_SUCCESS


def _shortList_HELPER_LS(path: str, green: str, reset: str) -> tuple[str, int]:
    """
    Short listing.
    > param path: Path of directory to be listed
    > param green: ANSI code for green
    > param reset: ANSI code for reset
    > return: String to be printed and error code (ref. src\\errCodes.txt)
    """
    toRet : list[str]
    toJoin: list[str]
    toRet      = []
    toRetApp   = toRet.append
    termSz     = os.get_terminal_size().columns
    gutter     = 2
    entries    = [(entry.name, entry.is_file()) for entry in os.scandir(path)]
    entriesLen = len(entries)

    if not entries:
        return '', comm.ERR_SUCCESS

    for cols in range(entriesLen, 0, -1):
        rows      = math.ceil(entriesLen / cols)
        colWidths = [0] * cols

        for idx, (nm, _) in enumerate(entries):
            col            = idx // rows
            dispNm         = f"\"{nm}\"" if ' ' in nm else nm
            colWidths[col] = max(colWidths[col], len(dispNm))

        totalColWidth = sum(width + gutter for width in colWidths)
        if totalColWidth <= termSz:
            break

    table = [[('', False)] * cols for _ in range(rows)]
    for idx, (nm, isFl) in enumerate(entries):
        row             = idx % rows
        col             = idx // rows
        table[row][col] = (nm, isFl)

    for row in table:
        toJoin    = list()
        toJoinApp = toJoin.append
        for i, (nm, isFl) in enumerate(row):
            g = green if isFl else ''
            r = reset if isFl else ''
            if not i:
                if ' ' in nm:
                    toJoinApp(g + f"\"{nm}\"".ljust(colWidths[i] + 1) + r)
                else:
                    toJoinApp(g + ' ' * (gutter - 1) + nm.ljust(colWidths[i]) + r)
                continue

            if ' ' in nm:
                toJoinApp(g + ' ' * (gutter - 1) + f"\"{nm}\"".ljust(colWidths[i] + 1) + r)
            else:
                toJoinApp(g + ' ' * (gutter) + nm.ljust(colWidths[i]) + r)

        toRetApp(''.join(toJoin).rstrip())

    return '\n'.join(toRet), comm.ERR_SUCCESS


def singleDirLS(path: str, longL: bool, green, yellow, reset,
                whichDt: str = "created") -> tuple[str, int]:
    """
    Single directory listing.
    > param path: Path of the directory to be examined
    > param longL: Do long listing?
    > param whichDt: Determine date type to be used (created/modified)
    > param lastNl: Print/omit last newline in short listing
    > return: Error code (ref. src\\errCodes.txt)
    """
    string = ''
    try:
        if longL:
            string, err = _longList_HELPER_LS(path, green, yellow, reset, whichDt)
        else:
            string, err = _shortList_HELPER_LS(path, green, reset)
    except PermissionError:
        comm.ERR(f"Access is denied: \"{path}\"", sl=4)
        err = comm.ERR_PERMDENIED
    return string, err


def LS(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
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
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'l', 'm', 'h', "-long", "-modified", "-help"}
    fls       = []
    dirs      = []
    toPrn     = []
    flsApp    = fls.append
    dirsApp   = dirs.append
    toPrnApp  = toPrn.append
    longL     = False
    modified  = False
    err       = comm.ERR_SUCCESS

    bold      = comm.ANSIBOLD   if op == '' else ''
    green     = comm.ANSIGREEN  if op == '' else ''
    yellow    = comm.ANSIYELLOW if op == '' else ''
    reset     = comm.ANSIRESET  if op == '' else ''

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for opt in optVals:
            if opt == 'l' or opt == "-long":
                longL = True
            elif opt == 'm' or opt == "-modified":
                modified = True
        if modified and not longL:
            comm.ERR("Modified option must be used with long listing option")
            return comm.ERR_INCOPTUSAGE

    if not args:
        tmp = singleDirLS('.', longL, green, yellow, reset,
                          "modified" if modified else "created")
        err = err or tmp[1]
        toPrnApp(bold + str(pl.Path('.').resolve()) + reset)
        if tmp[1] == 0 and tmp[0]:
            toPrnApp(tmp[0])

    for arg in args.values():
        if os.path.isdir(arg):
            dirsApp(arg)
        elif os.path.isfile(arg):
            flsApp(arg)
        elif not os.path.exists(arg):
            comm.ERR(f"No such file/directory: \"{arg}\"")
            err = err or comm.ERR_NOFLDIR

    maxSzFls = float("inf")
    if op == '':
        maxSzFls = max((len(str(os.path.getsize(fl))) for fl in fls), default=0)

    # Files are processed first...
    for fl in fls:
        flNm = green + str(pl.Path(fl).resolve()) + reset
        if not longL:
            toPrnApp(flNm)
            continue
        itemData = os.stat(fl)
        toPrnApp("{} {} {} {}".format(
            yellow + stat.filemode(itemData.st_mode) + reset,
            dt.datetime.fromtimestamp(
                itemData.st_birthtime
            ).strftime(r"%d-%m-%Y %H:%M"),
            f"{itemData.st_size:<{maxSzFls}}",
            flNm
        ))

    toPrnApp('') if fls and dirs else None
    lenDirs = len(dirs)

    # ... then come the directories!
    for idx, dir_ in enumerate(dirs):
        tmp = singleDirLS(dir_, longL, green, yellow, reset,
                          "modified" if modified else "created")
        err = err or tmp[1]
        if tmp[1] != 0:
            continue

        toPrnApp(bold + str(pl.Path(dir_).resolve()) + reset)
        if tmp[0]:
            toPrnApp(tmp[0])
        toPrnApp('') if idx < lenDirs - 1 else None

    if toPrn:
        print('\n'.join(toPrn))

    return err
