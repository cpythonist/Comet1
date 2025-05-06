#
# Comet 1 standard library command
# Filename: src\\bin\\sleep.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import time
import typing as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9c5N\xb1\x0e\x82@\x14\x9by_\xd1\x1f8\xdc\xdd\x18\x08:\x08F \x0e\x86\xe1\xc4\x07\\\x02\xef\x08w\xc4\xf8\xf7\x1e\x18\x976i\x9b\xb6wm<4Z^\xbc6\x02=\xd9U<l\x07o&\xc6\x93;\xbb0Z+\xde\xc8j\xa4\x8f\x89\xea2\xc9\xd2#\xdc\xc8<\xe3\xa1\x86&\x804\xbf|\x1c\x87@r\xcb\xeaK\x9aW%m\x1aE\xd5\xe6x\x8b\xf76\x156\x1c\x87\xbe\x97#*\xae\xd5\xb9\xc8KR\x03\x0ePj\xe0q\xa6\xe8\x14\x10\x13;\xa7{&%\xbb#\xd6\x9b\xeeCQ\xbe3V\xc7\xcb\xff\xda~\xe3\x0b\xb3\x03?<"

ERR_INVTIMEVAL      = 104
ERR_TIMEVALTOOLARGE = 133


def SLEEP(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
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
    validOpts = {'n', 'h', "-notify", "-help"}
    notify    = False
    err       = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for opt in optVals:
            if opt == 'n' or opt == '-notify':
                notify = True

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    times = []
    for arg in args.values():
        try:
            times.append(float(arg))
        except ValueError:
            comm.ERR(f"Invalid time value: '{arg}'")
            return ERR_INVTIMEVAL

    for validArg in times:
        if notify:
            stream.write(f"Sleeping {validArg}s...\n")
            stream.flush()
        try:
            time.sleep(float(validArg))
        except OverflowError:
            comm.ERR(f"Time value too large: {validArg}; skipping...")
            err = err or ERR_TIMEVALTOOLARGE

    return err
