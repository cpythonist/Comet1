#
# Comet 1 standard library command
# Filename: src\\bin\\dir.py
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
    b"x\x9cE\x8f\xcdj\xc3@\x0c\x84\xcf\xd6S\xcc\x0b\xac{\xef\xcd\x107-4v\x88"
    b"\xd7\xa7\x90\xc3\xc6V\xbb\x0b\xfec\xa5\x06\x9c\xa7\xef\xa6u\xe9e\x18\r"
    b"\x9aOh\x17d\x19\xdc*P\xcf\xe8\xe6IyR\xc1<1\x06\xbe\xf1\x800I\xe8\x19\x0e}"
    b"\x88\xdc\xe9\x1c\xd7\x9c\xa8m\x8a}\xf9\xfc\x88p6\xfe\x82\xf3\xe2\xd4#\xcf"
    b"\xf3\x0bQq\xda\xb7\x87\xb2\xb2\rU\x89B\xd9{\x10\xdd\xe8_1&\xfa?\x89\x1e5"
    b"\xcav\x7f3t\xc65\x1dN\r\xee\x89\xea\xa3}\xab\xab\x86\x8c\xc7\x13\x8c\xf1<"
    b",\x94\xbd&\xc5\xc8\"\xee\x93\xd3Jk\x8f\xad\xc5K}:\x14\x96\xba\xc8N\xd9"
    b"\xf4I\xb0y\r#c\x9c\xfb\xf0\xb1\xfe\xe6\x9b\xff\xc9u]\x18\x12\xee\x8c\xc9"
    b"\x8d\x89V\xd5\xb6\xa4&\xcd\x02\x179\xbd\x8e\xeb\xaa,\xdf-\'`\xe4"
)


def singleDIR(path: str, bold: str, green: str, yellow: str,
              reset: str) -> tuple[str, int]:
    """
    Print info about the directory given.
    > param path: Path of the directory
    > return: Error code (ref. src\\errCodes.txt)
    """
    try:
        toReturn    = []
        toReturnApp = toReturn.append
        toReturnApp(bold + (path := str(pl.Path(path).resolve())) + reset)

        with os.scandir(path) as iter_:
            entries = [(entry, entry.stat()) for entry in iter_]

        maxSz = max([len(str(i[1].st_size)) for i in entries], default=1)
        cnt = 0

        for entry, itemData in entries:
            isFl     = entry.is_file()
            sz       = itemData.st_size if isFl else ''
            type_    = "FL" if isFl else "DIR"
            created  = dt.datetime.fromtimestamp(
                itemData.st_birthtime
            ).strftime(r'%d-%m-%Y %H:%M:%S')
            modified = dt.datetime.fromtimestamp(
                itemData.st_mtime
            ).strftime(r'%d-%m-%Y %H:%M:%S')

            toReturnApp(f"{created} {yellow}{modified}{reset} {type_:<3} "
                        f"{sz:>{maxSz}} {green}{entry.name}{reset}")
            cnt += 1

        return '\n'.join(toReturn), comm.ERR_SUCCESS

    except FileNotFoundError as e:
        comm.ERR(f"Directory modified before dir executed: \"{path}\"", sl=4)
        return '', comm.ERR_NODIR

    except PermissionError:
        comm.ERR(f"Access is denied to directory: \"{path}\"", sl=4)
        return '', comm.ERR_PERMDENIED

    except OSError:
        comm.ERR(f"Operation failed; invalid path, directory "
                 f"\"{path}\" in use or unescaped characters?", sl=4)
        return '', comm.ERR_OSERR


def DIR(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
        args: dict[int, str], opts: dict[int, str], fullCmd: str,
        stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Displays the contents one level inside a directory.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'h', "-help"}
    toPrn     = []
    toPrnApp  = toPrn.append
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

    if not args:
        tmp = singleDIR('.', bold, green, yellow, reset)
        if tmp[1] == 0:
            toPrn.append(tmp[0])

    for dir_ in args.values():
        if not os.path.isdir(dir_):
            comm.ERR(f"No such directory: \"{dir_}\"")
            err = err or comm.ERR_NODIR
            continue

        tmp = singleDIR(dir_, bold, green, yellow, reset)
        err = err or tmp[1]
        if tmp[1] != 0:
            continue
        toPrnApp(tmp[0])

    print('\n'.join(toPrn)) if toPrn else None

    return err
