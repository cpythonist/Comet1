#
# Comet 1 standard library command
# Filename: src\\bin\\echo.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import typing as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9cU\x8e\xb1\x0e\x82@\x10Dk\xf6+\xb6\xa3:\xec\xb5\"\x91\xa0\x85`\x04*C"
    b"\x81\xbar$\xc7\xdd\x85=c\xfc{\x17\xa4\xb1\x99lv^f&\xbbkG\x8c\x1dr\x98\x06"
    b"\xdb\'\x00M\x95\xe6\xd9\x16I\x0c\xbc*\xdd\x8a02y\x01\xe4\x16\xc5$IZ\x80"
    b"\xf4\x927\xa7\xac\xa8+(\x9c%\x88\xb25\xc9\"\x8d>|\xd0\x0c\xf2\x15\x1c\xa2"
    b"j\x89\xc6\xe0\xf0FK.=\xe0\x17(\x1e\xf9n\xea\xc2\xe0\xec\xba`\x87\xe3\x8b"
    b"\x03>\x9d1\xee\x8d\xb1toP)\xc1ct~\xe6\x00\xcas},\x8b\n\x94^<M\xc6Ct\x10"
    b"\xc5\x91\x98\xbb\x9e@1D{z\xca\x82y\xf9\x7f\xc1\x17\xb2KN5"
)


def ECHO(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Echoes a string or writes a string to a file.
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
    sep       = ' '
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'s', 'h', "-sep", "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        sOptGiven = False, ''
        for opt in opts.keys():
            if opts[opt].lower() == 's' or opts[opt].lower() == "-sep":
                if sOptGiven[0]:
                    comm.ERR(f"-{sOptGiven[1]} was already given")
                    return comm.ERR_INCOPTUSAGE
                try:
                    sep = args[opt + 1]
                    args.pop(opt + 1)
                except KeyError:
                    comm.ERR(f"-{opts[opt]} must be followed by separation "
                             "string")
                    return comm.ERR_INCOPTUSAGE
                sOptGiven = True, opts[opt]

    print(*(args.values()), sep=sep)
    return comm.ERR_SUCCESS
