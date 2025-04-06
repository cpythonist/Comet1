#
# Comet 1 standard library command
# Filename: src\\bin\\sdu.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import pathlib as pl
import typing  as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Calculates the disc usage of files/directories.", '',
    "USAGE: du [-h] [-r[1 | 2 | 3]] path ...", '', "ARGUMENTS", "path",
    "\tFile/directory to calculate disc usage for", '', "OPTIONS",
    "-h / --help", "\tHelp message", "-r[1 | 2 | 3]",
    "\t'Human-readable' memory values", "\tNone - best unit",
    "\t1 - kilobytes (1000 B)", "\t2 - megabytes (1000 kB)",
    "\t3 - gigabytes (1000 MB)"
)


def _calcDirDU_HELPER_DU(stream, path: str) -> tuple[int, bool]:
    totalSz  = 0
    snagsHit = False

    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                totalSz += os.stat(comm.PTHJN(root, file)).st_size
            except FileNotFoundError:
                comm.WARN(f"Skipping \"{comm.PTHJN(root, file)}\"; "
                          "non-existant file", sl=4)
                snagsHit = True
            except PermissionError:
                comm.WARN(f"Skipping: \"{comm.PTHJN(root, file)}\"; "
                          "access is denied", sl=4)
                snagsHit = True

    return totalSz, snagsHit


def DU(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
       args: dict[int, str], opts: dict[int, str], fullComm: str,
       stream: ty.TextIO, op: str) -> int:
    """
    Calculates the disk usage of a file/directory.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-4) (ref. src\\errCodes.txt)
    """
    optVals      = comm.LOWERLT(opts.values())
    validOpts    = {'r', "r1", "r2", "r3", 'h', "-help"}
    szAlphas     = ('', 'k', 'M', 'G')
    formatChosen = False
    num          = 0
    err          = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt[0] == 'r':
                if formatChosen:
                    comm.ERR("Cannot accept multiple format options")
                    return 3
                num          = int(rem if (rem := opt[1:]) != '' else 4)
                formatChosen = True

    if not args:
        comm.ERR("Incorrect format")
        return 1

    snagsHit = False
    for arg in args.values():
        if os.path.isdir(arg):
            sz, snagsHit = _calcDirDU_HELPER_DU(stream, arg)
        elif os.path.isfile(arg):
            try:
                sz = os.stat(arg).st_size
            except FileNotFoundError:
                comm.WARN(f"Skipping \"{arg}\"; non-existant file", sl=4)
                snagsHit = True
                continue
            except PermissionError:
                comm.WARN(f"Skipping: \"{arg}\"; access is denied", sl=4)
                snagsHit = True
                continue
        else:
            comm.ERR(f"No such file/directory: \"{arg}\"")
            err = err or 4
            continue

        alpha = ''
        if num == 4:
            szLen = len(str(sz))
            if szLen > 9:
                sz    /= 1000000000
                alpha  = 'G'
            elif szLen > 6:
                sz    /= 1000000
                alpha  = 'M'
            elif szLen > 3:
                sz    /= 1000
                alpha  = 'k'
        else:
            sz    /= 10 ** (num * 3)
            alpha  = szAlphas[num]

        print(f"\"{pl.Path(arg).resolve()}\" {round(sz, 3)}{alpha}B")
        if snagsHit:
            comm.WARN("Issues encountered while processing; may be incorrect")

    return err
