#
# Comet 1 standard library command
# Filename: src\\bin\\start.py
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

helpStr = b"x\x9c=\x8d=\x0f\x820\x18\x84g\xde_qa\xd2\xc4\xe2\xee\xc6@\x94A0|L\xc6\xa1\xc0\xab4\x81\x96\xb4%\xd1\x7f/`\xe2r\xc9\xdds\x97\xcb'\xd6\x0e\xbb\xd0yi\xbd\x0b\xf7\x90x\xaa\x81\x0f\xe8\x94\xe5\xd6\x1b\xfb\x81\xb1\xe07\xb7\xb3\x97\xcd\xc0\x11Q]\xc6\xe7\xe4\x84m\x81\xbb\xe8\x1fP\x9eGD\xd1\xc2\xe2\xe2\\_\x93\xac*i\xcd(HW\xe2\r\x1a\x86Y\x9e\xb8#\xcaoU\x9ag%eF3\x05\xc5\xac!\x1d\xda\xd9Z\xd6\x1e\xb3cKB\xe2\x08!d7*\xfdo\xfc\x9c\xe87\xd4\xf30QpY\x14#;'_\xfc\x05\xde>>i"


def START(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
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
    validOpts = {'a', 'h',
                 "-admin", "-help"}
    admin     = False
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS
        for opt in optVals:
            if opt == 'a' or opt == "-admin":
                admin = True

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    for arg in args.values():
        try:
            os.startfile(arg, "runas") if admin else os.startfile(arg)

        except FileNotFoundError:
            try:
                if admin:
                    os.startfile(str(pl.Path(arg).resolve()), "runas")
                else:
                    os.startfile(str(pl.Path(arg).resolve()))

            except FileNotFoundError:
                comm.ERR(f"No such file/directory/executable: '{arg}'")
                err = err or comm.ERR_NOFLDIR

        except PermissionError:
            comm.ERR(f"Access is denied: '{arg}'")
            err = err or comm.ERR_PERMDENIED

        except OSError:
            comm.ERR("Operation failed; invalid name/path or unescaped "
                     "characters or operation cancelled?")
            err = err or comm.ERR_OSERR

    return err
