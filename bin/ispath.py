#
# Comet 1 standard library command
# Filename: src\\bin\\ispath.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import pathlib as pl
import typing  as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9c\x85\x90\xcdN\xc30\x10\x84\xcf\xd9\xa7\x98\x17pz\xe7VUQ\xe1@Z\x91\xf6\x84z0\xc9\xa4\xb6h\xed*v\x0bH<<\xb6\x85@\xfc\x08.+{w\xfc\xcd\x8e\x17\x86\xfdc\xc0\xe8'DC\xf0\xd9\x86\xa8]O\xf8\x11\x1a'\x1dM-\xb2\xed\xe6\xcb\xe6\n6\xe4;\xee\x95\xd9\xa52\xe2\x15j\xc8'\xee\x8a\x10u\x9d\xb4\xf3\xbb\xe5\xf6\xb6i7\x9d\xe4\x9eT\xeb<I\xb0\xd1\x1e\x88\xe8\xf1@\xf4\xd9\x93\x83\xc8j\xbd\xb9Y\xb5\x9d\xb4\xdeQ\xaa\xc5\xe7*\xdf\xd6\xc8og\x83\x9d\xd8G?\xbd\xe0\xc9&\xe4\xde^\xe8\xe0\xf4\x91\xa2\x06\xcc\xa0\xd4\x87\xe0\x0b\xea\x97T\x7f\x90XHE\x1f\xa4j\\8O\x0c\x89\xa1c\x01\x95\x98\xef\xd3\xf4\x01I\x9bW\xfb\xcf\xafD\xffae\x8a\x95\xe1\xe1$\xd5u\xaa82\x04\xbd\xe7\x1b\xa6\x13\x84\x0e"


def ISPATH(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
           args: dict[int, str], opts: dict[int, str], fullCmd: str,
           stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Checks for the existance of a path.
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
    optVals         = comm.LOWERLT(opts.values())
    validOpts       = {'f', 'd', 'e', 'h',
                       "-file", "-directory", "-exists", "-help"}
    optAlreadyGiven = False
    func            = os.path.exists
    mustExist       = False
    err             = comm.ERR_SUCCESS

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS
        for opt in optVals:
            if opt not in ('f', 'd', "-file", "-directory"):
                continue
            if optAlreadyGiven:
                comm.ERR("Check option already given")
                return comm.ERR_INCOPTUSAGE
            if opt == 'f' or opt == "-file":
                func = os.path.isfile
            elif opt == 'd' or opt == "-directory":
                func = os.path.isdir
            optAlreadyGiven = True
        # -e option
        mustExist = True if 'e' in optVals else False

    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    for arg in args.values():
        res = func(arg)
        if mustExist and not os.path.exists(arg):
            comm.ERR(f"Does not exist: \"{arg}\"")
            err = err or comm.ERR_NOFLDIR
        else:
            print(f"\"{pl.Path(arg).resolve()}\"", res)

    return err
