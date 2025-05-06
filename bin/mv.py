#
# Comet 1 standard library command
# Filename: src\\bin\\mv.py
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

helpStr = b"x\x9c]\x8c\xbd\n\x830\x14\x85g\xefS\x9c\x17H\xdd\xbb\t\x15\xe9\xe0\x0f\x8dN\xa5C\x88\xb7M@\x8d$\xa9\xe0\xdb7u\xe8\xd0\xe5\xc09|\xdf\xa9\xdd\xc6\x01\nO;1\x9c\xc7h=\xeb\xe8\xfc~\"\x1adQ\x95g\xcc\x1b\xee\xc2<\x10\xbc\xc6\xc8!\x12\x15\xb7j\xa8\xcb\xa6\x97\x946\xca\xa4{{\xcd\xc7E\xfe\xf3\xe9@\xb3KJ\xbb\xa8h\xdd\xf2\x0fP\xdb\xf5\xd7\xb6\x91$\x0cr\x08axZ\x93`\xc3:\xa9\x1d\xdf\x86\x99CP/\xfe\x00\x81\xdd6Z"


def MV(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Moves a file or directory.
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

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

    if len(args) != 2:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    src = args[sorted(args)[0]]
    dst = args[sorted(args)[1]]
    try:
        sh.move(src, dst)
    except FileNotFoundError:
        comm.ERR(f"No such file/directory: \"{src}\"")
        return comm.ERR_NOFLDIR
    except PermissionError:
        comm.ERR("Access is denied")
        return comm.ERR_PERMDENIED

    return comm.ERR_SUCCESS
