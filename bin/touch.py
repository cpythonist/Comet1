#
# Comet 1 standard library command
# Filename: src\\bin\\touch.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import pathlib as pl
import typing  as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9cs.JM,I-V\xd0P*\xc9/M\xceH-V\xd2THT\xc8K-WH\xcb\xccI\xd5\xe3\xe2\n\rvtw\xb5R\x00\xcb*D\xebf\xc4\x82%\x14\xf4\xf4\x80r\x8eA\xee\xa1\xbe\xae~!\xc1\\ 1.N7 \x99\x97\x98\x9b\xaa\x90\x96_\xa4P\x92\x91\n7\x87\x8b\xcb? \xc4\xd3\xdf/\x98K7CA_AW7#5\xa7\x80\x8b\xd3\x03H*\xe4\xa6\x16\x17'\xa6\xa7\x02\x00L\x0b)\xba"


def TOUCH(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
          args: dict[int, str], opts: dict[int, str], fullCmd: str,
          stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Wait a certain amount of time before continuing.
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

    for path in args.values():
        if os.path.isfile(path):
            comm.ERR(f"File exists: {pl.Path(path).resolve()}")
            err = err or comm.ERR_FLDIREXISTS
            continue
        elif os.path.isdir(path):
            comm.ERR(f"Directory exists: {pl.Path(path).resolve()}")
            err = err or comm.ERR_FLDIREXISTS
            continue

        try:
            open(path, 'w').close()
        except PermissionError:
            comm.ERR(f"Access is denied to touch: {pl.Path(path).resolve()}")
            err = err or comm.ERR_PERMDENIED
        except OSError:
            comm.ERR("Operation failed; invalid filename, disc full or "
                     "unescaped characters?")
            err = err or comm.ERR_OSERR

    return err
