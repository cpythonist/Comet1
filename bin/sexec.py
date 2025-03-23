#
# Comet 1 standard library command
# Filename: bin\\sexec.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License
#

import os
import sys
import traceback as tb
import typing    as ty

# Add "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Executes a string in the CPython-3.12.6 interpreter.",
    "USAGE: exec [-h] string ...", "ARGUMENT(S)", "\tstring",
    "\t\tString(s) to be executed in the CPython interpreter",
    "OPTION(S)", "\t-h / --help", "\t\tHelp message"
)


def EXEC(interpreter: comet.Interpreter, command: str, args: dict[int, str],
         opts: dict[int, str], fullComm: str, stream: ty.TextIO,
         op: str) -> int:
    """
    Executes a string in the CPython-3.12.6 interpreter.
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2) (ref. src\\errCodes.txt)
    """
    optVals   = comm.lowerLT(opts.values())
    validOpts = {'h', "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if not args:
        comm.ERR("Incorrect format")
        return 1

    for code in args.values():
        tmpStream = sys.stdout
        try:
            sys.stdout = stream
            exec(code)
        except:
            print(tb.format_exc())
        finally:
            sys.stdout = tmpStream

    return 0
