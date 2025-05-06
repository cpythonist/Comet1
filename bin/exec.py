#
# Comet 1 standard library command
# Filename: src\\bin\\exec.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import traceback as tb
import typing    as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9c]\x8d\xbd\n\xc20\x14\x85\xe7\xde\xa78/\x90\x88\n\x0enEJ\xeb`[L;"
    b"\x89C\xd5KS\xd0\xb4$\x11\xf4\xed\xbd\xea\".g\xf8\xce_\xf6\xe0\xf3=r@\x87"
    b"\x10\xfd\xe0z\x0c\x0e\xd126\xf53\xda\xd1\xa9\xa5\x9e/\xf4Jhd?y\x16\xd5D"
    b"\xadI\xf3l\r\x962\x0e\xca\x1e\xdf]h-N\xba\xcf\xdb]V6\x86\x04Qb\xbe\x9bq"
    b"\xc4\x89?q\xf9\xba\xfc]\xfcn\x13Uu\xb3\xadJC\xcab\x06\xa5,_\'J\nQ\xdc8"
    b"\x84\xae\xe7\x17.\xc99F"
)


def EXEC(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Executes a string in the CPython-3.12.6 interpreter.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
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

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    for code in args.values():
        tmpStream = sys.stdout
        try:
            sys.stdout = stream
            exec(code)
        except:
            print(tb.format_exc())
        finally:
            sys.stdout = tmpStream

    return comm.ERR_SUCCESS
