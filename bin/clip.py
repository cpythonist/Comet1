#
# Comet 1 standard library command
# Filename: src\\bin\\clip.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import subprocess as sp
import typing     as ty

# Add directory "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9c-\x8e\xb1\x0e\x830\x10Cg\xee+\xee\x07\x92\xee\xddP\x8bh\x87B\xd5"
    b"\xc0T1\x84r%\x91 \x89r\xf9\x7f5A]<X\xf6\xb3/>Xb\xe4\x14\xad[\x19\x93\xc7"
    b"d\x08?\x9b\r\xb3\xd7q\x91\x00\xa3\xaa\xdb\xe6|X\xf8\x16f\xca\x92\xf3\x14"
    b"\xa6RB)s\xa4~\xb5\xe3\xa3\xe9\x06\x05\xd9\x82J\x1d\xb0\xc2\x9a3\xaa\x0c,"
    b"\x00\xfds\xb8\xf7\x9d\x02a\xf0\x84B\x18\xda\x02T\xb7\xac\xb8\x13\xb3^\t"
    b"\x04Cu\xa5\xafuT\xf0:\xead\xbd\xfb?\xfb\x01q`5'"
)


def CLIP(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
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
    validOpts = {'h', 's', "-sep", "-help"}
    sep       = ' '
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for pos in opts:
            opt = opts[pos].lower()
            if opt == 's' or opt == "-sep":
                if pos + 1 not in args:
                    comm.ERR(f"One argument must follow -{opt}")
                    return comm.ERR_INCOPTUSAGE
                sep = args[pos + 1]
                args.pop(pos + 1)

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    sp.run(["clip.exe"], input=sep.join(args.values()), check=True, text=True)
    return err
