#
# Comet 1 standard library command
# Filename: src\\bin\\sshutdown.py
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
    "Shuts down the computer.", '',
    "USAGE: shutdown [-h] [-s | -r] [-y] [-t time]", '',
    "ARGUMENTS", "time", "\tTime to wait to execute command", '',
    "OPTIONS", "-h / --help", "\tDisplay help message",
    "-r / --restart", "\tRestart the computer", "-s / --shutdown",
    "\tShutdown the computer", "-t / --time",
    "\tTime period to wait (integer)", "-y / --hybrid",
    "\tEnables hybrid mode while startup."
)

def SHUTDOWN(varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
    """
    Shuts down the computer.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
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
    optVals   = comm.LOWERLT(opts.values())
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
