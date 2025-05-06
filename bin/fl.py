#
# Comet 1 standard library command
# Filename: src\\bin\\fl.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import mimetypes as mt
import pathlib   as pl
import typing    as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9cU\x8e\xbdn\x83@\x10\x84\xeb\xdb\xa7\x98\xce\xa68\x02v\x97\xceV,;"
    b"\x85\xb1\x15\xec\nQ\x1ca\x81\x93\x8f\x1fqG\x14\xa4<|\x0e\xa5\x89\x8b\x1d"
    b"i\xe6\xdb\xd5\xec\x9b\xb6\x83Q\xb3\x85k\x18n\x1e\x18}\x05\x85A\xb9\x06"
    b"\xebJ\x1b\xefG\x94z\xe4O\xd7\x8fs\x10\x12\xdd\xd3\xdd\xf1\xf0\x8a\xca "
    b"\x93M\xeee\xccb\xfc`\xe3g\x9b\xe7\x7f\x97Y\x18\x869\xd1\xee\xe3x?\x1f"
    b"\x92[JKJ\xe2\xba0\xd7\xa3`\xf0\xb7ju\xc7%\xd1\xe5z{\xbf$)\xc9\x06/\x90"
    b"\xb2a3\x908yE\xcb\xd6\xaa\x9a\xe9\xa9\x81\xc4\xea4\xb5\xaa\x93#\xabR\x15"
    b"\x86W~\xaf\xf5\xbf\xe1K\x99\x89-\x89\xa4\xef\x18\xd2\x97X\x87\xa9\xd3\x8e"
    b"D\xec\xedC\x9b\xbe\x98\x1d[\xac\xe3(\x8a\xb0\x0fHl|\xder\xad\xfe\xe7\x8f"
    b"\x05l=\xa8\xf538\xef\x83_\\\xe9Y\x08"
)


def _HELPER_FL(givenFlOrDir: str, num: int) -> tuple[tuple[str, str, str], int]:
    """
    Helper function of the FL function. For printing item information of a
    single item.
    > param givenFlOrDir: Path to be examined
    > param num: 'Human-readable' memory values (10 ** x)
    > return: Error code (ref. src\\errCodes.txt)
    """
    sz: float

    try:
        # Get type_ of fl
        type_ = mt.guess_type(givenFlOrDir)

        if os.path.isfile(givenFlOrDir):
            sz    = os.path.getsize(givenFlOrDir)
            alpha = ''
            if num == 4:
                szLen = len(str(sz))
                if szLen > 9:
                    sz    /= 1000000000
                    alpha  = 'G'
                elif szLen > 6:
                    sz    /= 1000000
                    alpha  = 'M'
                elif szLen > 3:
                    sz    /= 1000
                    alpha  = 'k'
            else:
                alpha = ('', 'k', 'M', 'G')[num]
                sz   /= 1000 ** num

            sz = round(sz, 2)
            if sz == int(sz):
                sz = int(sz)
            return (
                str(pl.Path(givenFlOrDir).resolve()),
                (type_[0] if type_[0] is not None else "unknown"),
                str(sz) + f"{alpha}B"
            ), comm.ERR_SUCCESS

        elif os.path.isdir(givenFlOrDir):
            return (str(pl.Path(givenFlOrDir).resolve()),
                    "directory", '-'), comm.ERR_SUCCESS

        else:
            # Will be caught in the except block
            raise FileNotFoundError

    except FileNotFoundError:
        comm.ERR(f"No such file/directory: \"{givenFlOrDir}\"", sl=4)
        return ('', '', ''), comm.ERR_NOFLDIR

    except PermissionError:
        comm.ERR(f"Access is denied: \"{givenFlOrDir}\"", sl=4)
        return ('', '', ''), comm.ERR_PERMDENIED

    except OSError:
        comm.ERR(f"Operation failed; invalid name, file/directory in use or "
                 "unescaped characters?", sl=4)
        return ('', '', ''), comm.ERR_OSERR


def FL(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Displays the type of a path (file or directory).
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
    toPrn: list[tuple[str, str, str]]
    optVals      = comm.LOWERLT(opts.values())
    validOpts    = {'r', "r1", "r2", "r3", 'h', "-help"}
    formatChosen = False
    num          = 0
    toPrn        = []
    toPrnApp     = toPrn.append
    err          = comm.ERR_SUCCESS
    green        = comm.ANSIGREEN if op == '' else ''
    reset        = comm.ANSIRESET if op == '' else ''

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS
        for opt in optVals:
            if opt[0] == 'r':
                if formatChosen:
                    comm.ERR("Cannot accept multiple format options")
                    return comm.ERR_INCOPTUSAGE
                num          = int(rem if (rem := opt[1:]) != '' else 4)
                formatChosen = True

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    col1Max = 0
    col2Max = 0
    col3Max = 0
    for arg in args.values():
        tmp2 = _HELPER_FL(arg, num)
        if tmp2[1]:
            err = err or tmp2[1]
            continue

        toPrnApp((tmp2[0][1], tmp2[0][2], tmp2[0][0]))
        col1Max = max(col1Max, len(tmp2[0][1]))
        col2Max = max(col2Max, len(tmp2[0][2]))
        col3Max = max(col3Max, len(tmp2[0][0]))

    col1Max = 0 if op != '' else col1Max
    col2Max = 0 if op != '' else col2Max
    col3Max = 0 if op != '' else col3Max

    for tup in toPrn:
        print(f"{green}{tup[0]:<{col1Max}}{reset}  {tup[1]:>{col2Max}}  "
              f"{tup[2]:<{col3Max}}")

    return err
