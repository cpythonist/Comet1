#
# Comet 1 standard library command
# Filename: src\\bin\\find.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import re
import sys
import typing as ty

# Add "src\\core" to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    b"x\x9ce\x8e\xb1\x0e\x820\x10\x86g\xee)\xee\x05\xaa\xbb\x1bQB\x1c\x14Ca2"
    b"\x0c\x15\x0e\xda\x04\n\xe9U\x83oo\xcb\xa2\x89\xcb\r_\xee\xff\xfe?'\xcf8)"
    b"\xdfjb\xecg\x87\n\x1d\r\xcfQ9\xa4uq\xc4lf\x8b\xc6\x06\xce\xde\x19;\xec"
    b"\x00j\x99\xe6\xd9\x01{c;\xbc\x0b\xdd\x84\xd361Fk|\x02H\xcb\xbc\xbed\xd7J"
    b"\xc2\x06!)\xff\x95\xb1k\xeb\rN\x88\xa9Dn~\xf43>\x08\x99\x94\x0b\x9b\xbaP"
    b"\rP\xdc\xaasq\x95 Z\xdc\xa3\x10\xadb2\x96\xc9\xb2\xf1\xe6E\x90\x1c\x03"
    b"\x10?\xe4+\x16zKh\x1a\x17HN\x86\x97Q\xbd\xd1k\xc2Hp\n[\xd4@\x1f\xc2\xf3W"
    b"\xa1"
)


def FIND(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Searches for a substring in a string given.
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
    toPrn: list[str]
    reqLn: list[str]
    optVals   = comm.LOWERLT(opts)
    validOpts = {'c', 'h', "-casesensitive", "-help"}
    caseIn    = False
    toPrn     = []
    toPrnApp  = toPrn.append
    green     = comm.ANSIGREEN if op == '' else ''
    reset     = comm.ANSIRESET if op == '' else ''

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS
        for opt in optVals:
            if opt == 'c' or opt == "-casesensitive":
                caseIn = True

    if len(args) != 2:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    argVals   = tuple(args.values())
    regex     = re.escape(argVals[0])
    string    = argVals[1]
    pattern   = re.compile(regex) if not caseIn else regex
    regexfunc = re.finditer
    regexflag = re.IGNORECASE if caseIn else 0

    lns = string.split('\n')
    for ln in lns:
        allSpans = []
        spans    = []

        for match in regexfunc(pattern, ln, regexflag):
            allSpans.append(match.span())

        if allSpans == []:
            continue

        for i in allSpans:
            spans += list(range(*i))

        reqLn    = []
        reqLnApp = reqLn.append
        for idx, char in enumerate(ln):
            colour = idx in spans
            reqLnApp((green if colour else '') + char + (reset if colour else ''))

        toPrnApp(''.join(reqLn))

    if toPrn:
        print('\n'.join(toPrn))

    return comm.ERR_SUCCESS
