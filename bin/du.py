#
# Comet 1 standard library command
# Filename: src\\bin\\du.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
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

helpStr = (
    b"x\x9cU\x8f?o\xc20\x10\xc5g\xdf\xa7\xb8\x8d28$\xb0u\x83\x8aB\x07B\xd5\xc0"
    b"\x8428\xc9%\xb6pb\xe4?\x95\x90\xfa\xe1k\x0f\xad`\xb8\'\xdd{O\xf7\xd3\xbd"
    b"\t\xdd\x06-<9\xf4\x92\xb0S\xae\xc5\xe0\xc4@hz\xec\x95&\xb7\xe8\x94\xa5"
    b"\xd6\x1b\xab\xc8e\x00\xe7j\xbd\xdb\xbeb\x17\xf0\xc2e\x1d\xc5^\n\xfc\xc1e"
    b"\x9cU]\xe3Mx\x89Y\x16\x8b\xeb\xaf\xdd\xf9\xb0-O\x15$\x0f\xd8{<\xf6\x7f"
    b"\xeb\x8e\xde`\xfb\xc7~\xc4\xf6\xc6\x02\x1c?O\x1f\xc7\xb2\x02.q\x81\x9cK"
    b"\xd27`\xfb\xa88\x92K5x\xc2\x02\x9b\xed\xc3(&nIt\xa2\xd14\x8b\xbd1Q\xbe"
    b"\x85\x0e\xe4\x80\x95f\"\xe4\xd8\x90\xf3\x18&\xe5\x81\x15q\xbd*m\x9a{\xfa"
    b"\xfd\xa5\xc8\xf3\x1c7s`\xcb\xe8\x8f4\x88G\xff\x9a\x82U\x0c\x06\xf5\x1c"
    b"\x1c6\xf3_\xff0a\xa1"
)


def _calcDirDU_HELPER_DU(stream, path: str) -> tuple[int, bool]:
    totalSz  = 0
    snagsHit = False

    for root, _, files in os.walk(path):
        for file in files:
            try:
                totalSz += os.stat(os.path.join(root, file)).st_size
            except FileNotFoundError:
                comm.WARN(f"Skipping \"{os.path.join(root, file)}\"; "
                          "non-existant file", sl=4)
                snagsHit = True
            except PermissionError:
                comm.WARN(f"Skipping: \"{os.path.join(root, file)}\"; "
                          "access is denied", sl=4)
                snagsHit = True

    return totalSz, snagsHit


def DU(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Calculates the disk usage of a file/directory.
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
    toPrn: list[tuple[str, str]]
    optVals      = comm.LOWERLT(opts.values())
    validOpts    = {'r', "r1", "r2", "r3", 'h', "-help"}
    szAlphas     = ('', 'k', 'M', 'G')
    toPrn        = []
    toPrnApp     = toPrn.append
    maxSz        = 0
    formatChosen = False
    num          = 0
    err          = comm.ERR_SUCCESS
    green        = comm.ANSIGREEN if op == '' else ''
    reset        = comm.ANSIRESET  if op == '' else ''

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

    snagsHit = False
    for arg in args.values():
        if os.path.isdir(arg):
            sz, snagsHit = _calcDirDU_HELPER_DU(stream, arg)
        elif os.path.isfile(arg):
            try:
                sz = os.stat(arg).st_size
            except FileNotFoundError:
                comm.WARN(f"Skipping \"{arg}\"; non-existant file", sl=4)
                snagsHit = True
                continue
            except PermissionError:
                comm.WARN(f"Skipping: \"{arg}\"; access is denied", sl=4)
                snagsHit = True
                continue
        else:
            comm.ERR(f"No such file/directory: \"{arg}\"")
            err = err or comm.ERR_NOFLDIR
            continue

        alpha = ''
        if num == 4:
            szLen  = len(str(sz))
            lens_  = [9, 6, 3]
            alphas = ['G', 'M', 'k']
            for i, len_ in enumerate(lens_):
                if szLen > len_:
                    sz    /= 10 ** len_
                    alpha  = alphas[i]
                    break
        else:
            sz    /= 10 ** (num * 3)
            alpha  = szAlphas[num]

        sz = round(sz, 3)
        if sz == int(sz):
            sz = int(sz)

        maxSz = max(maxSz, len(str(sz) + alpha) + 1)

        toPrnApp((f"{sz}{alpha}B", str(pl.Path(arg).resolve())))
        if snagsHit:
            comm.WARN(f"Issues encountered while processing \"{arg}\"; "
                      "may be incorrect")

    if toPrn:
        print('\n'.join(f"{green}{i[0]:<{maxSz}}{reset} {i[1]}" for i in toPrn))
    return err
