#
# Comet 1 standard library command
# Filename: src\\bin\\tail.py
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

helpStr = b"x\x9cm\x8e=\x0e\xc20\x0cF\xe7\xfa\x14\xbe@`g\xabD)\x0c\xa4\x88\xb6\x13\xea\x90\xaa\x0e\x89\x94\xfe\xa8\x0eBpz\x92\xc0\xc8\xf2\xc9\xb6\xec\xf7\xbc\xb7\xbc8\xf5b\xf4\x86\xd0)\xf6\xa8\xe9\x89\xceN\xc48kT\xa8\xad\xa3\r@[\xe7e\xb1C\xaf\xac\xc3\x9b0]\x08F\xb6o\xea\xd2\x06@~-\xdbs!\x9b\x1aR\x9f\x1dB\xa2\x9f\xb1'\x1c\xbe\x0e\x1a\x00\xaaKs\xaad\r\xe1x\x8bBD\x00d\xf21\xf6\xb4F\xddO\xac\xd7yL\x0f\xd14\xc4q,\xf5?\x9e0\tc\xc8-\x90\x1dC\xe2H\xcc\xeaN\x1f\x08KD\xb4"

ERR_INVPEEKSZ = 134


def TAIL(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Displays the last few lines of a file.
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
    validOpts = {'s', 'h', "-size", "-help"}
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
            opt      = opts[pos]
            optLower = opt.lower()

            if optLower == 's' or optLower == "-size":
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
        with open(fl, 'r', buffering=1) as f:
            noOfLns = 1
            for ln in f:
                noOfLns += 1
            f.seek(0)
            for i, ln in enumerate(f):
                if i < noOfLns - peekSz - 1:
                    continue
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
