#
# Comet 1 standard library command
# Filename: src\\bin\\kill.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import subprocess as sp
import typing     as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9cm\x90\xbd\x0e\x82@\x10\x84k\xf6)\xa6\xd4b\xb1\xb73\xd1(!\xfeD\xb42\x14x\xecy\x17O \x1c\x16&>\xbc\x87F-\xb4\x99bf\xe7\xcbfR\xeb\x9cG\xd3\xd6J\xbc\x17\x1f\x13\xed\xb3\xc9|6\xc69\x048\xb0\xc9\x83\xe8^T\x8e\xc1\x81+\xdc\xc16\x7f6\x86\x88\xe3P\x98l\xe7\xfb\xe5l\xb5\xcb\xa87)\xda\xbc`\xa8\x8a\x8b\xa0n\xdfp$St5\x8e\xf2DKI\xb4\xde\xec\x92\xf5*#6\x18\x81\xd9\x88k(Z\x04\xc5%\xdc\x17'!\xae(\xca\x1aQV\xdf>\x98\x1eKl\x7f\x83dJ\xac)J\xfb\xc7;#\x1f_\xd7\xad\x12}u\xeeF\xac\xfe\xe4EU\xc2v\x1e\xcaXW~\xa7x\x00M\xcbZl"

ERR_NOSUCHPROC = 109


def KILL(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Kills processes.
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
    validOpts = {'n', 'i', 'f', "kc", 'h',
                 "-name", "-pid", "-force", "-killchildren", "-help"}
    call      = ["taskkill"]
    lookup    = {
        'n': "/im",
        'i': "/pid",
        'f': "/f",
        "kc": "/t",
        "-name": "/im",
        "-pid": "/pid",
        "-force": "/f",
        "-killchildren": "/t"
    }
    specOpts  = {'n', 'i', "-name", "-pid"}
    allProcs  = []
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for optNo in opts:
            if opts[optNo].lower() in specOpts:
                # Check if an argument follows the option
                if optNo + 1 not in args:
                    comm.ERR(f"One argument must follow -{opts[optNo]}")
                    return comm.ERR_INCOPTUSAGE
                allProcs.append([lookup[opts[optNo].lower()], args[optNo + 1]])
            else:
                call.append(lookup[opts[optNo]].lower())

    if not opts or not args \
            or not specOpts.intersection(set(comm.LOWERLT(opts.values()))):
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    for procArr in allProcs:
        call2 = list(call)
        try:
            call2.extend(procArr)
            sp.run(call2, capture_output=True, check=True)
        except sp.CalledProcessError as e:
            # 128: Process not found
            # 1: Access is denied
            if e.returncode == 128:
                comm.ERR(f"No such process: '{procArr[1]}'")
                err = err or ERR_NOSUCHPROC
            elif e.returncode == 1:
                comm.ERR(f"Access is denied: '{procArr[1]}'")
                err = err or comm.ERR_PERMDENIED
            else:
                comm.ERR("Operation failed; unknown cause\n"
                         f"Return: {e.returncode}")
                err = err or comm.ERR_OSERR

    return err
