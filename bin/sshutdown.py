#
# Comet 1 standard library command
# Filename: bin\\sshutdown.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import subprocess as sp
import typing     as ty

srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Shuts down the computer.", "USAGE: shutdown [-h] [-s | -r] [-y] [-t time]",
    "ARGUMENT(S)", "\ttime", "\t\tTime to wait to execute command",
    "OPTION(S)", "\t-h / --help", "\t\tDisplay help message",
    "\t-r / --restart", "\t\tRestart the computer", "\t-s / --shutdown",
    "\t\tShutdown the computer", "\t-t / --time",
    "\t\tTime period to wait (integer)", "\t-y / --hybrid",
    "\t\tEnables hybrid mode while startup."
)

def SHUTDOWN(interpreter: comet.Interpreter, command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
    """
    Shuts down the computer.
    > param interpreter: Interpreter object
    > param command: Command name
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-3, 114) (ref. src\\errCodes.txt)
    Error code 114:
        Invalid time value (expected int)
    """
    optVals   = comm.lowerLT(opts.values())
    validOpts = {'s', 'r', 'y', 't', 'h',
                 "-shutdown", "-restart", "-hybrid", "-time", "-help"}
    toDo      = ''
    time      = 0
    hybrid    = False

    if not opts:
        comm.ERR("Incorrect format")
        return 1

    if tmp := (set(optVals) - validOpts):
        comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
        return 2
    if 'h' in optVals or "-help" in optVals:
        print(comm.CONSHELPSTR(helpStr))
        return 0
    for pos in opts:
        opt = opts[pos]
        if opt == 's' or opt == "-shutdown":
            toDo = "shutdown"
        elif opt == 'r' or opt == "-restart":
            toDo = "restart"
        elif opt == 't' or opt == "-time":
            if pos + 1 not in args:
                comm.ERR(f"One argument must follow {opt}")
                return 3
            try:
                if '.' in args[pos + 1]:
                    # No floats. I said let there be integers, and there
                    # shall only be integers!
                    raise ValueError
                time = int(args[pos + 1])
            except ValueError:
                comm.ERR(f"Invalid time value: '{args[pos + 1]}'")
                return 114
        elif opt == 'y' or opt == "-hybrid":
            hybrid = True

    if toDo == '':
        comm.ERR("Incorrect format")
        return 1

    toExecute = ["shutdown"]
    if toDo == "shutdown":
        toExecute.append("/s")
    elif toDo == "restart":
        toExecute.append("/r")
    if hybrid:
        toExecute.append("/hybrid")
    toExecute.extend(("/t", str(time)))

    output = sp.run(toExecute, check=True, text=True)
    return 0
