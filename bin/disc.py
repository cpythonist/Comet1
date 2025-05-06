#
# Comet 1 standard library command
# Filename: src\\bin\\disc.py
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
    b"x\x9c%\x8d\xcb\n\xc20\x10E\xd7\xceW\xccR\x17\xf1\xb1\xd4]\xc1\xfaX\xd8"
    b"\x14\x9b\xaeD!\xb5\xd3&\x90>\xc8D\xa1~\xbdA7\x97\xcb=\x07\xee\xde\xf2\xe8"
    b"\xf4\xc4\x18\x0cam\xf9\x89\xb6o\x06\xdf\xe9`\x87~\tP\x16\xc91\xdd\xfd\xc9"
    b"M\x98;\x80\xcc\xd5Yf\x05\x08\x83+\x14\xc2\x90\x1bav\x8a\x89\x1d1\xeb\x96"
    b"\xa2R\xaa\xbcTx\x90\xd7K\xa2\xa0\xf6\xf6M\x18\x86\xa0\x1d\xbe\x98jl<E)"
    b"\x93*\x85\xc49d\xfb!F\xed)^ck[]M!\x0e\xf3\xcd\xfa\xb1\xc5__|\x01=\x8d4"
    b"\xc9"
)


def DISC(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
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
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'h', "-help"}
    green     = comm.ANSIGREEN if op == '' else ''
    reset     = comm.ANSIRESET if op == '' else ''

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

    if args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

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
        print(f"{green}{sz[0]}{reset} "       # Drive letter
              f"{sz[1][0]:>{maxSzTotal}} "    # Total
              f"{sz[1][1]:>{maxSzUsed}} "     # Used
              f"{sz[1][2]:>{maxSzFree}}")     # Free

    return comm.ERR_SUCCESS
