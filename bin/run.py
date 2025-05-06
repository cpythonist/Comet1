#
# Comet 1 standard library command
# Filename: src\\bin\\run.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import pathlib as pl
import typing  as ty

# Add src\\core to sys.path
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)) + os.sep + "core")
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9c\x0b*\xcdSHT(N.\xca,(\xd1\xe3\xe2\n\rvtw\xb5R(\x02\x8aF\xebf\xc4*\xa4e\xe6\xa4rq9\x06\xb9\x87\xfa\xba\xfa\x85\x04s\x81\xf9\x9c\xc1`\xe5`I\x85\x92|\x85\xa4T\x90\x06..\xff\x80\x10O\x7f\xbf`.\xdd\x0c\x05}\x05]\xdd\x8c\xd4\x9c\x02.N\x0f \xa9\x90\x9bZ\\\x9c\x98\x9e\n\x00\x14\xbe!\x0c"


def RUN(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
        args: dict[int, str], opts: dict[int, str], fullCmd: str,
        stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Run a script.
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
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'h', "-help"}
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    for arg in args:
        if not os.path.isfile(arg):
            comm.ERR(f"No such file: {arg}")
            err = err or comm.ERR_NOFL
            continue

        with open(arg, 'r', buffering=1) as f:
            pass

    return err
