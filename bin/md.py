#
# Comet 1 standard library command
# Filename: src\\bin\\md.py
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

helpStr = b"x\x9cs.JM,I-VHT\xc8K-WH\xc9,JM.\xc9/\xaa\xd4\xe3\xe2\n\rvtw\xb5R\xc8MQ\x88\xd6\xcd\x88U\xc8K\xccMU\xd0\xd3\x03J8\x06\xb9\x87\xfa\xba\xfa\x85\x04s\x81\xc4\xb88\xfd@2\xf9i\n%\x19\xa9\xa8\x86hd\xa6\x16krq\xf9\x07\x84x\xfa\xfb\x05s\xe9f(\xe8+\xe8\xeaf\xa4\xe6\x14pqz\x00I\x85\xdc\xd4\xe2\xe2\xc4\xf4T\x00\xa2L(\xa4"


def MD(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Creates a new directory.
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

    for arg in args.values():
        try:
            os.makedirs(arg)

        except FileExistsError:
            if os.path.isdir(arg):
                comm.ERR("Directory exists: "
                         f"\"{pl.Path(arg).resolve()}\"")
            else:
                comm.ERR(f"File exists: \"{pl.Path(arg).resolve()}\"")
            err = err or comm.ERR_FLDIREXISTS

        except PermissionError:
            comm.ERR(f"Access is denied: \"{pl.Path(arg).resolve()}\"")
            err = err or comm.ERR_PERMDENIED

        except OSError:
            comm.ERR(f"Operation failed while processing \"{arg}\"; invalid "
                     "path, disc full or unescaped characters?")
            err = err or comm.ERR_OSERR

    return err
