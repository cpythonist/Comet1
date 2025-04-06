#
# Comet 1 standard library command
# Filename: src\\bin\\sgreet.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import datetime as dt
import typing   as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Greets the user.", '', "USAGE: greet [-h] [-1 | -2 | -3] [name]", '',
    "ARGUMENTS", "None", "\tUse username as name", "name", "\tCustom name",
    '', "OPTIONS", "-h / --help", "\tHelp message", "-1",
    "\tFormat: Good (morning | afternoon | evening | night), (user)",
    "-2", "\tFormat: Hello, (user)"
)

def GREET(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
          args: dict[int, str], opts: dict[int, str], fullComm: str,
          stream: ty.TextIO, op: str) -> int:
    """
    Greets the user.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2, 102) (ref. src\\errCodes.txt)
    Error code 102:
        Invalid time. Should never happen. But, just in case, as I am
        incompetent.
    """
    optVals         = comm.LOWERLT(opts.values())
    validOpts       = {'1', '2', 'h', "-help"}
    optAlreadyGiven = False
    arg             = None
    opt             = None

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for i in optVals:
            if optAlreadyGiven:
                comm.ERR("Multiple format options received")
                return 3
            if i == '1':
                opt = '1'
            elif i == '2':
                opt = '2'
            optAlreadyGiven = True

    if args:
        if len(args) != 1:
            comm.ERR("Incorrect format")
            return 1
        arg = args[sorted(args)[0]]

    time = int(dt.datetime.now().strftime("%H"))
    if time in range(12):
        time = "morning"
    elif time in range(12, 16):
        time = "afternoon"
    elif time in range(16, 24):
        time = "evening"
    else:
        # Should never be executed, but if it does get executed... well, time is fucked
        comm.ERR("Invalid time? WHAT?!")
        return 102

    if opt == '1' or opt is None:
        print(f"Good {time}, {os.getlogin() if arg is None else arg}!")
    else:
        print(f"Hello, {os.getlogin() if arg is None else arg}!")

    return 0
