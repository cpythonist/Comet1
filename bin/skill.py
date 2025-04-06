#
# Comet 1 standard library command
# Filename: src\\bin\\skill.py
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

helpStr = (
    "Kills the specified process(es).", '',
    "USAGE: kill [-h] [-f] [-c] ([-n | -i] proc) ...", '', "ARGUMENTS",
    "proc", "\tProcess name or process ID to be killed", '',
    "OPTIONS", "-h / --help", "\tHelp message", "-n",
    "\tSpecify process name", "-i", "\tSpecify process ID", "-f",
    "\tKill the process forcefully", "-c",
    "\tKill the process and its child processes"
)


def KILL(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
         args: dict[int, str], opts: dict[int, str], fullComm: str,
         stream: ty.TextIO, op: str) -> int:
    """
    Kills the specified process(es).
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-3, 5-6, 109) (ref. src\\errCodes.txt)
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
    specOpts = {'n', 'i', "-name", "-pid"}
    allProcs = []
    err      = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for optNo in opts:
            if opts[optNo].lower() in specOpts:
                # Check if an argument follows the option
                if optNo + 1 not in args:
                    comm.ERR(f"One argument must follow -{opts[optNo]}")
                    return 3
                allProcs.append([lookup[opts[optNo].lower()], args[optNo + 1]])
            else:
                call.append(lookup[opts[optNo]].lower())

    if not opts or not args \
            or not specOpts.intersection(set(comm.LOWERLT(opts.values()))):
        comm.ERR("Incorrect format")
        return 1

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
                err = err or 109
            elif e.returncode == 1:
                comm.ERR(f"Access is denied: '{procArr[1]}'")
                err = err or 5
            else:
                comm.ERR("Operation failed; unknown cause\n"
                         f"Return: {e.returncode}")
                err = err or 6

    return err
