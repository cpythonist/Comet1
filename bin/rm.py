#
# Comet 1 standard library command
# Filename: src\\bin\\rm.py
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

helpStr = b"x\x9c]\x8d;\x0e\x830\x10Dk\xef)\xf6\x02\x86>\x1d\x05\")B\x10\x9f*\xa2 \xf1\x12[\x02\x8c\xd6\x0eRn\x9f\x05)M\x9aW\xcc\x1b\xcd\xd44\xfb\x8d\x02\x8en\x12\x0e\x8bA\xe3\x98\x9e\xd1\xb3\xa3\x90\x00tMV\xe4\'\xe4\x19\xef\xda\xf6\x02\xeeq\x1d\xa2\xc5$\x11\x9b\xd5Ew\xcd\xcb\xb6\x81=\x03U\xed\xc6\x8f\xc7Z\xfa\x1b\xfa`\xf4\xf8 \xe4\xe3\xca\x00\xdc\xaa\xf6r+\x1b(\xfdB\xa0\x84Z\x8ao\x0en#44Q$\xd0\x16S\xd4\xda\xd2\xb4\x82:\x0bq\xa6\x10\x86\x97\x18\x06U\xff\xd5\xbf\x8d\xf5?\xaf"


def RM(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Removes a file/directory.
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
    > return: Error code (0-6) (ref. src\\errCodes.txt)
    """
    recurse   = False
    optVals   = opts.values()
    validOpts = {'r', 'h', "-recurse", "-help"}
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS
        for opt in optVals:
            if opt in ('r', "-recurse"):
                recurse = True

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    for idx in sorted(args):
        arg = args[idx]

        try:
            if os.path.isfile(arg):
                os.remove(arg)
            elif os.path.isdir(arg) and recurse:
                sh.rmtree(arg)
            elif os.path.isdir(arg) and not recurse:
                comm.ERR(f"Cannot remove \"{arg}\": Is a directory; use -r "
                         "option")
                err = err or comm.ERR_INCOPTUSAGE
            else:
                comm.ERR(f"No such file/directory: \"{arg}\"")
                err = err or comm.ERR_NOFLDIR

        except PermissionError:
            comm.ERR(f"Access is denied: \"{arg}\"")
            err = err or comm.ERR_PERMDENIED

        except FileNotFoundError:
            comm.ERR(f"No such file/directory: \"{arg}\"")
            err = err or comm.ERR_NOFLDIR

        except OSError:
            comm.ERR("Operation failed: invalid path, file/directory in use "
                     "or unescaped characters?")
            err = err or comm.ERR_OSERR

    return err
