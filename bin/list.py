#
# Comet 1 standard library command
# Filename: src\\bin\\list.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import re
import sys
import subprocess as sp
import typing     as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9c]\x8d\xc1\x0e\x820\x10D\xcf\xecW\xec\x0f\xb4\xde\xbd\x91H\x90D\x81\x08\x9c\x0c\x07\x82\x8b%\xa1\xb4i\xeb\xc1\xbf\xb7\xad\xe8\x81\xcbdw\xde\xec\xcee\xb6\xce\xa22hi0\xa3 \x8b\x93_\xb4Q#YK\x96\x03tM\x9agG\\|\x10\xefL\xf4^\xd6 :\x88\xf4\xb2\x85\x91s\xde\x03\xa4\xb7\xbc\xbbfe\xdb\xc0\xe6C\xd2\n\xc2u\x90\x84jB\xe7\xe7\xdf\x81S[k\xe8\x04\xa8\xea\xb6\xa8\xca\x06\x98\xc0\x032&h\xd1\x90\x9c\xbd\xa2\xf4\xe9\xe1I\xc0\xd6H\xc2/Hj3\xaf\xee\xff+zl\x8e\\\xcf\x8f=.N\xc0d\x84\x92\xa42\xef=\xff\xba\xf8\n5\x1fl|W\xf5"


def _NOARGS_HELPER_LIST(names: list[str], ids: list[str], mems: list[str],
                        prnProcNames: bool, prnProcIDS: bool,
                        prnProcMems: bool) -> int:
    """
    Helper function for LIST when no arguments are given.
    > param names: List of process names
    > param ids: List of process IDs
    > param mems: List of process memory usages
    > param prnProcNames: Print process names?
    > param prnProcIDS: Print process IDs?
    > param prnProcMems: Print process memory usages?
    > return: Error code (ref. src\\errCodes.txt)
    """
    paddingNames = len(max(names, key=len))
    paddingIDS   = len(max(ids, key=len))
    paddingMems  = len(max(mems, key=len))

    for i in range(len(names)):
        prev = ''
        # I'm sorry for this. I had to do it because the command is already
        # slow and I had to make it push out every bit of performance it can
        if prnProcNames:
            (
                print(f"{names[i]:<{paddingNames}}", end='')
                if prnProcIDS or prnProcMems else
                print(names[i], end='')
            )
            prev = ' '

        if prnProcIDS:
            if prnProcNames:
                print(f"{prev}{ids[i]:>{paddingIDS}}", end='')
            else:
                (
                    print(f"{prev}{ids[i]:<{paddingIDS}}", end='')
                    if prnProcMems else
                    print(f"{prev}{ids[i]}", end='')
                )
            prev = ' '

        # Unnecessary comment, but I am writing it here for myself.
        # procList[2].strip()[:-2] removes whitespace and strips char 'K' from
        # TASKLIST O/P. Then cast to int, mul by 1024 then div by 1000 to get
        # true value in KB. Cast again to int to discard decimal point
        if prnProcMems:
            mem = str(int(int(mems[i].strip()[:-2]) * 1024 / 1000)) + "kB"
            (
                print(f"{prev}{mem:>{paddingMems}}", end='')
                if prnProcIDS else
                print(f"{prev}{mem}", end='')
            )

        print()

    return comm.ERR_SUCCESS


def _ARGS_HELPER_LIST(args: dict[int, str], names: list[str], ids: list[str],
                      mems: list[str], prnProcNames: bool, prnProcIDS: bool,
                      prnProcMems: bool, command: str) -> int:
    """
    Helper function for LIST when arguments are given.
    > param args: Dictionary of arguments
    > param names: List of process names
    > param ids: List of process IDs
    > param mems: List of process memory usages
    > param prnProcNames: Print process names?
    > param prnProcIDS: Print process IDs?
    > param prnProcMems: Print process memory usages?
    > param command: Command name
    > return: Error code (ref. src\\errCodes.txt)
    """
    required: list[tuple[str, str, str] | str]
    paddingNames = 0
    paddingIDS   = 0
    paddingMems  = 0
    required     = []
    requiredApp  = required.append
    err          = 0
    for arg in args.values():
        found = False
        for i, name in enumerate(names):
            if arg.lower() != name.lower():
                continue
            requiredApp((name, ids[i], mems[i]))
            found = True
        if not found:
            requiredApp(f"No such process: '{arg}'")

    try:
        paddingNames = len(max([i[0] for i in required], key=len))
        paddingIDS   = len(max([i[1] for i in required], key=len))
        paddingMems  = len(max([i[2] for i in required], key=len))
    except ValueError:
        pass

    for procList in required:
        # I'm sorry for this. I had to do it because the command is already
        # slow and I had to make it push out every bit of performance it can
        if isinstance(procList, str):
            comm.ERR(procList, sl=4)
            err = err or 103
            continue

        prev = ''
        if prnProcNames:
            (
                print(f"{procList[0]:<{paddingNames}}", end='')
                if prnProcMems or prnProcIDS else
                print(procList[0], end='')
            )
            prev = ' '
        if prnProcIDS:
            if prnProcNames:
                print(f"{prev}{procList[1]:>{paddingIDS}}", end='')
            else:
                (
                    print(f"{prev}{procList[1]:<{paddingIDS}}", end='')
                    if prnProcMems else
                    print(f"{prev}{procList[1]}", end='')
                )
            prev = ' '

        # Unnecessary comment, but I am writing it here for myself.
        # procList[2].strip()[:-2] removes whitespace and strips char 'K' from
        # TASKLIST O/P. Then cast to int, mul by 1024 then div by 1000 to get
        # true value in KB. Cast again to int to discard decimal point
        if prnProcMems:
            mem = str(int(int(procList[2].strip()[:-2]) * 1024 / 1000))+ "KB"
            if prnProcIDS:
                print(f"{prev}{mem:>{paddingMems}}", end='')
            else:
                print(f"{prev}{mem}", end='')

        print()

    return comm.ERR_SUCCESS


def LIST(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Lists processes, or searches for processes.
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
    optVals       = comm.LOWERLT(opts.values())
    validOpts     = {'n', 'i', 'm', 'h',
                     "-name", "-pid", "-memory", "-help"}
    prnProcNames  = False
    prnProcIDS    = False
    printProcMems = False
    err           = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS
        for opt in optVals:
            if opt == 'n' or opt == "-name":
                prnProcNames = True
            elif opt == 'i' or opt == "-pid":
                prnProcIDS = True
            elif opt == 'm' or opt == "-memory":
                printProcMems = True
    else:
        prnProcNames  = True
        prnProcIDS    = True
        printProcMems = True

    names: list[str]
    ids  : list[str]
    mems : list[str]
    output        = sp.run(["TASKLIST"], capture_output=True)
    tasklist      = output.stdout.decode("utf-8").split('\n')
    regexTasklist = r"^(.+?)\s+(\d+)\s(.+)\s+(\d+)\s+(\d*,*\d+\sK).*$"
    names         = []
    ids           = []
    mems          = []
    namesApp      = names.append
    idsApp        = ids.append
    memsApp       = mems.append
    memsPop       = mems.pop
    memsIns       = mems.insert

    # Process tasklist command output
    for task in tasklist:
        matches = re.match(regexTasklist, task)
        if matches is not None:
            namesApp(matches.group(1))
            idsApp(matches.group(2))
            memsApp(matches.group(5))

    # Remove commas from memory values
    for i, memory in enumerate(mems):
        memsPop(i)
        memsIns(i, memory.replace(',', ''))

    if not args:
        err = _NOARGS_HELPER_LIST(names, ids, mems, prnProcNames,
                                  prnProcIDS, printProcMems)
    else:
        tmp2 = _ARGS_HELPER_LIST(args, names, ids, mems, prnProcNames,
                                 prnProcIDS, printProcMems, cmd)
        err  = err or tmp2

    return err
