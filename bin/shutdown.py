#
# Comet 1 standard library command
# Filename: src\\bin\\shutdown.py
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

helpStr = b"x\x9cU\x8e\xb1n\x021\x0c\x86\xe7\xf8)<\xb6C\xe8\xde\r\xa9\'\xd4\xa1P\x91cB\x0c\x81X$\xd2\xe5\x12%>]O\xea\xc3\x93\xdc\t\x04\xcb\x1f\xdb\xf9d\x7f\xca\x0e\x9c\xd1\x84\xb1G\xb6\x84\x97\xe0\xe3\xc0\x94V\x00\x07\xb5\xde4\x9f\x98\x0b0\x7f\x1f\xa5=\x95\xc8\xf8\x8f2\xd5j\xaa\xc1\xc8\xce\xd3\t`\xbd\xdf\x1c~\x9am\xab\xa0\x0e@\xb4%\x91\x03\x8e\xdaq}\xe9\x8f.es\xbd\xe0uo\x00v\xbf\xed\xf7n\xab@Z\xfc@)-u\x11\xc4\x97\xcb\xb1\xd3\x13\xd6\x0e=\xe5\xac\xaf\x042\xcdD\xa2\xcc:1\x88\xfdR\xbc\x08C\x11\xab\xd0]\x17\x84\xba\x8b\xbfb<cO\x8e\x91\x92\x0b\xe6\xa1\xfa\xe6z\xa6+\xa5w\x90\xd3\"6\x9d\x933 \x9a^\x9f;\xca\xb8\xf4\xe8\x83!\x1c\xad\xeb\x08g\x9b!\xaen\xda\xcdl\xa2"

ERR_INVTIMEVAL = 114


def SHUTDOWN(varTable: dict[str, str], origPth: str, prevErr: int,
             cmd: str, args: dict[int, str], opts: dict[int, str],
             fullCmd: str, stream: ty.TextIO, op: str, debug: bool) -> int:
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
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals   = comm.LOWERLT(opts.values())
    validOpts = {'s', 'r', 'y', 't', 'h',
                 "-shutdown", "-restart", "-hybrid", "-time", "-help"}
    toDo      = ''
    time      = 0
    hybrid    = False

    if not opts:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    if tmp := (set(optVals) - validOpts):
        comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
        return comm.ERR_UNKNOPTS
    if 'h' in optVals or "-help" in optVals:
        print(comm.DECOMPSTR(helpStr))
        return comm.ERR_SUCCESS
    for pos in opts:
        opt = opts[pos]
        if opt == 's' or opt == "-shutdown":
            toDo = "shutdown"
        elif opt == 'r' or opt == "-restart":
            toDo = "restart"
        elif opt == 't' or opt == "-time":
            if pos + 1 not in args:
                comm.ERR(f"One argument must follow {opt}")
                return comm.ERR_INCOPTUSAGE
            try:
                if '.' in args[pos + 1]:
                    # No floats. I said let there be integers, and there
                    # shall only be integers!
                    raise ValueError
                time = int(args[pos + 1])
            except ValueError:
                comm.ERR(f"Invalid time value: '{args[pos + 1]}'")
                return ERR_INVTIMEVAL
        elif opt == 'y' or opt == "-hybrid":
            hybrid = True

    if toDo == '':
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    toExecute = ["shutdown"]
    if toDo == "shutdown":
        toExecute.append("/s")
    elif toDo == "restart":
        toExecute.append("/r")
    if hybrid:
        toExecute.append("/hybrid")
    toExecute.extend(("/t", str(time)))

    try:
        sp.run(toExecute, check=True, text=True)
    except sp.CalledProcessError:
        comm.UNERR("Windows SHUTDOWN command failed; see the log for details",
                   raiser='c')
        return comm.ERR_UNKNOWN

    return comm.ERR_SUCCESS
