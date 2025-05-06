#
# Comet 1 standard library command
# Filename: src\\bin\\whoami.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import platform as pf
import typing   as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9cs\xc9,.\xc8I\xac,V(\xc9HUH.-*J\xcd+\xc9\xa9T\xc8\xc9OOOMQ\xc8\xccS(-N-\xd2\xe3\xe2\n\rvtw\xb5R(\xcf\xc8O\xcc\xcdT\x88\xd6\xcd\x88\xe5\xe2\xf2\x0f\x08\xf1\xf4\xf7\x0b\xe6\xd2\xcdP\xd0W\xd0\xd5\xcdH\xcd)\xe0\xe2\xf4\x00\x92\n\xb9\xa9\xc5\xc5\x89\xe9\xa9\x00\xcd%\x1e\x10"


def WHOAMI(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
           args: dict[int, str], opts: dict[int, str], fullCmd: str,
           stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Checks for the existance of a path.
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
    
    print(os.getlogin() + '@' + pf.node())
    return comm.ERR_SUCCESS
