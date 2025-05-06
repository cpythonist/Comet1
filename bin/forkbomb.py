#
# Comet 1 standard library command
# Filename: src\\bin\\forkbomb.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import subprocess as sp
import typing     as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9c\xf3*-.QHTH\xcb/\xcaVH\xca\xcfM\xd2\xe3\xe2\n\rvtw\xb5\x02\x0b\x81D"
    b"\x14\xa2u3b\xb9\xb8\xfc\x03B<\xfd\xfd\x82\xb9t3\x14\xf4\x15tu3Rs\n\xb88="
    b"\x80\xa4Bnjqqbz*\x00O\xdb\x16|"
)


def FORKBOMB(varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Just a fork bomb.
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
    validOpts = {'h', "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown options: {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

    if args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    print("It isn't what you thought it would be...")
    return comm.ERR_SUCCESS
