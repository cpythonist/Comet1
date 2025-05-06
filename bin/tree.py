#
# Comet 1 standard library command
# Filename: src\\bin\\tree.py
# Copyright (c) 2024, Infinite Inc.
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

helpStr = b"x\x9c]O\xb1n\xc20\x10\x9ds_q\x1bap\xbaw\xa3\x05Q\x86\x06T`\xaa\x18\x9c\xf8BN5vd;B\x91\xfa\xf1\xb5\x93\xa6H]\x9e\xf5\xee\xbd{~\xb7f\xdfi9x\x94\x18\x1c\x11\xda\x06\xa5\xd6\xe8\xfbJ\xb1\xa3:X\xc7\xe41\x97Fa\xc3\x9a\xfc\x12\xd9D\xef,\x0e\x05\xc0\xf9\xb8\xdan\x9e\xa7\xf5O\xd1^\"4\t*\xfcF1$\xe0H\xe3\x06\x16Eq\x01X}l\xcf\xef\x9b\xf2t\x84\xd2\x1a\x82\xec\xb5w\x8eL\xc0\xbbu_l\xae\x8fl\xf4m\xeaR\x11\xf6\x9e\x14\xc49d\xebY\xcc9\x95\xb9\xb7\\\xb7h\x88\x14\x06\x9b\x9c\x8bTc!\xa2\x1d\xf6\x87\xd3n_\xce\xbf\xbc\xc8\x10\x9d\xb6\x0f]\x1f v{B!\xaa4\xfb/5\xa34\x1e\x0b\xd9\xc1ql6\x11\xd1\x8eJK\xba\x83\xec-\"\xde\xc8{y%\x10<*ljG\xb7x\x8a\xd4\x90\xed\x1e\xe4/z\x98\x02\x86\xca\xb1\x8a\x11\xe3\x8by\xd57\r9R\xcb_\xdf\x0f!o\x82#"

ERR_INVFLUSHTHRESH = 111


def TREE(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
         args: dict[int, str], opts: dict[int, str], fullCmd: str,
         stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Displays a tree of all subdirectories (and files) inside a directory.
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
    # For prning files
    batch : list[str]
    hybrid: list[str]
    optVals        = comm.LOWERLT(opts.values())
    validOpts      = {'f', 'b', 'y', 'i', 'l', 'h', "-files", "-batch",
                      "-hybrid", "-incremental", "-flush", "-help"}
    flushOptGiven  = False
    argsFinIdx     = len(args) - 1
    prnFls         = False
    mode           = ''
    batch          = []
    batchApp       = batch.append
    err            = comm.ERR_SUCCESS
    bold           = comm.ANSIBOLD   if op == '' else ''
    green          = comm.ANSIGREEN  if op == '' else ''
    yellow         = comm.ANSIYELLOW if op == '' else ''
    reset          = comm.ANSIRESET  if op == '' else ''
    FILLCHRS       = '┊' + "   "
    ENDCHRS        = '├' + "───"
    FLUSHTHRESHOLD = 1000

    if not args:
        args = {-1: os.getcwd()}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for pos in opts:
            opt      = opts[pos]
            optLower = opt.lower()

            if optLower == 'f' or optLower == '-files':
                prnFls = True
                continue
            elif optLower == 'l' or optLower == "-flush":
                if pos + 1 not in args:
                    comm.ERR(f"Expected argument after -{opt}")
                    return comm.ERR_INCOPTUSAGE
                try:
                    tmp2 = int(args[pos + 1])
                except ValueError:
                    comm.ERR(f"Invalid value for flush threshold: '{args[pos + 1]}'")
                    return ERR_INVFLUSHTHRESH
                FLUSHTHRESHOLD = tmp2
                flushOptGiven  = True
                continue

            if mode:
                comm.ERR("Cannot use more than one mode")
                return comm.ERR_INCOPTUSAGE
            if optLower == 'y' or optLower == '-hybrid':
                mode = "hybrid"
            elif optLower == 'i' or optLower == '-incremental':
                mode = "incremental"
            elif optLower == 'b' or optLower == '-batch':
                mode = "batch"

        
        if flushOptGiven and mode != "hybrid":
            comm.ERR("Flush option can only be used with hybrid mode")
            return comm.ERR_INCOPTUSAGE

    else:
        mode = "batch"

    for i, arg in enumerate(args.values()):
        path    = str(pl.Path(arg).resolve())
        cnt     = 0
        # Find dir lvl in fl structure
        lvlArgs = path.count(os.sep)
        if not os.path.isdir(path):
            comm.ERR(f"No such directory: \"{path}\"")
            err = err or comm.ERR_NODIR
            continue

        hybrid    = []
        hybridApp = hybrid.append

        if mode == "batch":
            func = batchApp
        elif mode == "hybrid":
            func = hybridApp
        elif mode == "incremental":
            func = stream.write
        else:
            comm.UNERR("Unknown mode; not supposed to happen. Please "
                       "report to the developers", comm.GETEXC())
            return comm.ERR_UNKNOWN

        rootRes = path
        func(bold + path + reset)

        try:
            for root, _, files in os.walk(path):
                rootRes     = str(pl.Path(root).resolve())
                lvl         = (rootRes.count(os.sep)
                               - lvlArgs)
                fillIdnt    = (FILLCHRS) * (lvl - 1) + ENDCHRS
                fillSubidnt = (FILLCHRS) * (lvl) + ENDCHRS

                func(("{}{}{}".format(
                    fillIdnt,
                    os.path.basename(root),
                    yellow + os.sep + reset
                ) if cnt else '') + '\n')

                if prnFls:
                    for file in files:
                        func("{}{}{}{}".format(
                            fillSubidnt,
                            green,
                            os.path.basename(file),
                            reset
                        ) + '\n')

                if mode == "hybrid" and cnt % FLUSHTHRESHOLD == 0:
                    stream.write(''.join(hybrid))
                    hybrid.clear()

                cnt += 1

        except FileNotFoundError:
            comm.ERR(f"Race condition: directory \"{rootRes}\" modified before "
                     f"{cmd.lower()} executed")
            err = err or comm.ERR_RACECONDN
            continue

        # Flush any txt remaining in the buffer
        if hybrid and mode == "hybrid":
            stream.write(''.join(hybrid))

        # Prn at the end, if mode is batch o/p
        if mode == "batch":
            sys.stdout.write(''.join(batch))

        if i != argsFinIdx:
            sys.stdout.write('\n')

    return err
