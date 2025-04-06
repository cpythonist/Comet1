#
# Comet 1 standard library command
# Filename: src\\bin\\sdisc.py
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
    "Displays the disc information.", '', "USAGE: disc [-h]", '',
    "OPTIONS", "-h / --help", "\tHelp message", '',
    "OUTPUT FORMAT", "drive total used free", '',
    "NOTE", "All sizes are in gigabytes (10^9 bytes)"
)


def DISC(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
         args: dict[int, str], opts: dict[int, str], fullComm: str,
         stream: ty.TextIO, op: str) -> int:
    """
    Displays the disc information.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Command name
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2) (ref. src\\errCodes.txt)
    """
    optVals = comm.LOWERLT(opts.values())
    validOpts = {'h', "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if args:
        comm.ERR("Incorrect format")
        return 1

    allSzs      = []
    drives      = [f"{chr(i)}:\\" for i in range(65, 91)
                   if os.path.exists(f"{chr(i)}:\\")]
    maxSzTotal  = 3
    maxSzUsed   = 3
    maxSzFree   = 3
    for drive in drives:
        szs        = [str(round(i / 10 ** 9, 2)) for i in sh.disk_usage(drive)]
        maxSzTotal = max(len(szs[0]), maxSzTotal)
        maxSzUsed  = max(len(szs[1]), maxSzUsed)
        maxSzFree  = max(len(szs[2]), maxSzFree)
        allSzs.append((drive, szs))

    for sz in allSzs:
        if op == '':
            print(f"{sz[0]} "                   # Drive letter
                f"{sz[1][0]:>{maxSzTotal}} "    # Total
                f"{sz[1][1]:>{maxSzUsed}} "     # Used
                f"{sz[1][2]:>{maxSzFree}}")     # Free
        else:
            print(f"{sz[0]} {sz[1][0]} {sz[1][1]} {sz[1][2]}")

    return 0
