#
# Comet 1 standard library command
# Filename: src\\bin\\greet.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import datetime as dt
import typing   as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9cE\x8e\xbd\x0e\xc20\x0c\x84\xe7\xf8)<\x16\x89\x80\x80\xad[\x85\xa00P"
    b"\x10m'\xd4!\x12\xa6Ajb\x94\x04&\x1e\x9e\x84\x1f\xb1|\xb6\xef\xa4\xf3\x95"
    b"\x8e(x\x0c\x9a\xf0\xee\xc9M\x00\xda\xba(W9\xf6\xc9\xc0\x93\xd4]\xc4\x0c"
    b"\x9f(\xe7\t\x8bxZe\xa8\x03(\x8ee\xbb[UM\r\x15[\x02\xd1\xfaOF\xb2QyL\x13"
    b"\xde\x10\xcb\xbb\x0fl>\n\xec\x0f\xcdv_\xd5 5NQJM\xc3\r\xc4&\x12\ry\xafz"
    b"\x029\x03\xb1fgT\xc8\xb1d>cf\xd8\xd9\xab\xedc\x03u\t\xf1\x05\xb3\x8d;="
    b"\xe8\xab\xdak\xaf\xc3h\x8cY*0\x029\xff\x07\xc4\xe4\x81\x7f\xce\x0b5aJ\x0e"
)

ERR_INVTIMEWHAT = 102


def GREET(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
          args: dict[int, str], opts: dict[int, str], fullCmd: str,
          stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Greets the user.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals         = comm.LOWERLT(opts.values())
    validOpts       = {'1', '2', 'h', "-help"}
    optAlreadyGiven = False
    arg             = None
    opt             = None

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS
        for i in optVals:
            if optAlreadyGiven:
                comm.ERR("Multiple format options received")
                return comm.ERR_INCOPTUSAGE
            if i == '1':
                opt = '1'
            elif i == '2':
                opt = '2'
            optAlreadyGiven = True

    if args:
        if len(args) != 1:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        arg = args[sorted(args)[0]]

    time = int(dt.datetime.now().strftime("%H"))
    if time in range(12):
        time = "morning"
    elif time in range(12, 16):
        time = "afternoon"
    elif time in range(16, 24):
        time = "evening"
    else:
        # Should never execute, but if it does... well, time is done for
        comm.ERR("Invalid time? WHAT?!")
        return ERR_INVTIMEWHAT

    if opt == '1' or opt is None:
        print(f"Good {time}, {os.getlogin() if arg is None else arg}!")
    else:
        print(f"Hello, {os.getlogin() if arg is None else arg}!")

    return comm.ERR_SUCCESS
