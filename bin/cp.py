#
# Comet 1 standard library command
# Filename: src\\bin\\cp.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as sh
import typing as ty

# Add src\\core to sys.path temporarily
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9c]\x8d\xb1n\x021\x10D\xeb\xdb\xaf\x982\x14\x86\x9e&B\x80 \x05\xc7"
    b"\x89\x83\nQXf\x0f[\"\xde\xd3\xda\x17\x89\xbf\x8fu\xa0H\xa1y\xc5\xec\xbc"
    b"\xd9\xa5\xf4\x81\x13,\xbap\xe7\xd95(\xbb,\xfa@\x16\xd8(\xd9\xb3\xe2/\x9c"
    b"\x12\x9d\xda\xc5f=\x87\xebq6\xfeR\xa0\x17$u\xb8r\xcaD\x8b\xc3\xe6\xb4["
    b"\xd7\xc7\x96JFUc\xb3\x87tH2\xa8\xe3\xb7\x0f4*\xd5\xaa0D\x9b\x83Dt\xa2p"
    b"\xd2?B\xbc\xbd\x1c\xa2}s\xfc\xda\xd7-\xd5\x12\x99\xaaBS\xfcAS\xf8\xe1\xb1"
    b"\x8b\x8f\xcf\t\x19\x8f\x19\x8c\xf1|\xef\xa9\xda\x16\xe2\x9bS\xb27&\xa3"
    b"\xe3\xe5\xe9\x94\x81\xc3?\xf9\x17\x14\x98S\xc3"
)


def cpSrcToDest(src: str, dest: str) -> int:
    """
    > param src: Path of source file/directory
    > param dest: Destination for copying source
    > return: Error code (ref src\\errCodes.txt)
    """
    if not os.path.isdir(dest):
        comm.ERR(f"No such directory: \"{dest}\"", sl=4)
        return comm.ERR_NODIR
    if os.path.isfile(src):
        sh.copyfile(src, dest)
    elif os.path.isdir(src):
        sh.copytree(src, dest, dirs_exist_ok=True)
    else:
        comm.ERR(f"No such file/directory: \"{src}\"", sl=4)
        return comm.ERR_NOFLDIR
    return comm.ERR_SUCCESS


def CP(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Copies a file/directory to another directory.
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
    argsSorted = sorted(args)
    optVals    = comm.LOWERLT(opts.values())
    validOpts  = {'h', "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

    if len(args) != 2:
        comm.ERR(f"Incorrect format")
        return comm.ERR_INCFORMAT

    try:
        src = args[argsSorted[0]]
        dst = args[argsSorted[1]]
        err = cpSrcToDest(src, dst)
        return err

    except FileNotFoundError:
        comm.ERR("Race condition: Source or destination modified before "
                 "cp executed")
        return comm.ERR_RACECONDN

    except PermissionError:
        comm.ERR("Access is denied")
        return comm.ERR_PERMDENIED

    except OSError:
        comm.ERR("Operation failed; invalid path, access is denied, "
                 "the file/directory in use or unescaped characters?")
        return comm.ERR_OSERR
