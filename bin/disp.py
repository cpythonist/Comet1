#
# Comet 1 standard library command
# Filename: src\\bin\\disp.py
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

helpStr = (
    b"x\x9cu\x901o\xc20\x14\x84g\xde\xaf81\xb5\x83\xd3\x9d-\x12\x01:\x90 \xe2L"
    b"\x15\x83i^\x9a'%vT\x1b\xa9\xf4\xd7\xd7vE\xb7.7\xbc\xfb\xee\xa4{[\xf1\xcbd"
    b"\xee\x1ead\xbc;\x1b\xd8\x06\x0f7\xc0 \xf0W\xc0 \x13\x17D][\xee\xab\r\xfa_"
    b"\x1aoj\xbcD\x91K\xf6Q\x14\x11)\xcf\xfb\xeeX\xd5\xba\xa5t\xa3\xd5.9\xc1"
    b"\xe1\xca\x8f\x18\xf7D\xcdI\xbf6uK\xb5\xb3\x91\xd9:\xf6\xb0.\xfc\x15\xe7:"
    b"\xb1\x83\xfb\x9cM\x10gI\x8dx\x81R#O\x0b\xad\x0eQ1\xb3\xf7\xe6\x83IIv\x12"
    b"\x1c\x8b\xfe\xcbS\xd3\xe9S\xa7\xb1k\xce\xc7R\xd3:\x01\xd6\xcc\xbc&/\xdf"
    b"\x8c'\x19\x10\x8b\xdc\x92`\x88\xc7\xcds\xff\x9c\x17\xa8\xc77\x88\xeaFW"
    b"\x94\xf7\xe4P\xc4\xc4\xe2z\x0f\xec\x7f\x00\x16\x11g\x17"
)


def DISP(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Displays the contents of a text file.
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
    validOpts = {'i', 'p', 'h', "-info", "-path", "-help"}
    info      = False
    path      = False
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for opt in optVals:
            if opt == 'i' or opt == "-info":
                info = True
            elif opt == 'p' or opt == "-path":
                path = True

    if args == {} or len(args) >= 2:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    arg = args[sorted(args)[0]]
    if not os.path.isfile(arg):
        comm.ERR(f"No such file: \"{arg}\"")
        return comm.ERR_NOFL

    try:
        with open(arg, 'r', buffering=1) as f:
            sz  = os.path.getsize(arg)
            if sz == int(sz):
                sz = int(sz)

            print(pl.Path(arg).resolve()) if path else None
            print(f"Size: {sz} B") if info else None
            for line in f:
                print(line, end='')
            print()

    except FileNotFoundError:
        comm.ERR(f"No such file: \"{arg}\"")
        err = err or comm.ERR_NOFL

    except PermissionError:
        comm.ERR(f"Access is denied: \"{arg}\"")
        err = err or comm.ERR_PERMDENIED

    except OSError:
        comm.ERR("Operation failed; invalid path, file in use or unescaped characters?")
        err = err or comm.ERR_OSERR

    except UnicodeDecodeError:
        comm.ERR("Does not appear to contain text")
        err = err or comm.ERR_CANTDECODE

    return err
