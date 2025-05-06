#
# Comet 1 standard library command
# Filename: src\\bin\\head.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
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
    b"x\x9cm\x8e1\x0f\x820\x10\x85g\xeeW\xdc\x1f\xa8\xeen$\":\x08F`2\x0c%\\-"
    b"\xa1-\xa4-1\xfe{Kqppy\xc9\xdd}\xf7\xde;\x0enV\xfc\xed\xd0KB1X\xe7Q\xd0"
    b"\x0b\xd5`\xc8\xe1$\x90\x87\xa5\xa2\x1d@S\xa5yv@I\xbc\xc7\x07\x93m\x10\x83"
    b"f\xd1m\x04\x00\xd2{\xde\\\xb3\xa2\xae \xce\xc9)(\xfa\t;\xc2~\xcb\xa0\x1e"
    b"\x02\x0fI\xb1\xe8\x8e\xecj\xbe\xa5\x04h&\x1a\x01\xca[})\x8b\n\x82\xf1\x1e"
    b"\x193\x91\xfb\xe5\xbf\x0f\xc2N:\xf6u\x9e[\xbf\x1e\xb6\xf2\x7f\x02\x99\x8c"
    b"V\x92\xd4\x0c\xc99(jr\x8e?\xe9\x03\xf5\xa5P."
)

ERR_INVPEEKSZ = 134


def HEAD(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Displays the first few lines of a file.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Command name
    > param args: Arguments supplied to the command
    > param opts: Options supplied to the command
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'n', 'h', "-number", "-help"}
    peekSz    = None
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for pos in opts:
            opt  = opts[pos]
            optL = opt.lower()

            if optL == 'n' or optL == "-num":
                if peekSz is not None:
                    comm.ERR("Cannot specify peek size multiple times")
                    return comm.ERR_INCOPTUSAGE
                if pos + 1 not in args:
                    comm.ERR(f"Expected argument after -{opt}")
                    return comm.ERR_INCOPTUSAGE

                arg = args[pos + 1]
                args.pop(pos + 1)
                try:
                    peekSz = int(arg)
                except ValueError:
                    comm.ERR(f"Invalid peek size: '{arg}'")
                    return ERR_INVPEEKSZ
                if peekSz < 0:
                    comm.ERR(f"Invalid peek size: '{peekSz}'")
                    return ERR_INVPEEKSZ

    # ! Size argument is already removed
    if not args or len(args) > 1:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    if peekSz is None:
        peekSz = 5

    fl = args[sorted(args)[0]]

    try:
        with open(fl, 'r') as f:
            for i, ln in enumerate(f):
                if i > peekSz - 1:
                    break
                print(ln, end='')

    except FileNotFoundError:
        comm.ERR(f"No such file: \"{fl}\"")
        err = err or comm.ERR_NOFL

    except UnicodeDecodeError:
        comm.ERR(f"Does not appear to contain text: \"{fl}\"")
        err = err or comm.ERR_CANTDECODE

    except PermissionError:
        comm.ERR(f"Access is denied: \"{fl}\"")
        err = err or comm.ERR_PERMDENIED

    return err
