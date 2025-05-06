#
# Comet 1 standard library command
# Filename: src\\bin\\startup.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as sh
import typing as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = b"x\x9c]\xce\xcd\n\xc20\x0c\x07\xf0s\xf3\x14y\x81\xd6\xbb\xb7\xa1cxp\x93}\x9cd\x87\xe2\xa2-tX\x9a*\x08>\xbc\xdd\x14\xd1]B\xfe\xe1G\x92M \x1d\t5r\xd4!\xde<\xf2)X\x1f\x15@\xd7dE\xbe\xfe\xce\x8f\xd2\xf4\xa9\x84\x0f@\xa5\x14>Q\xf2O\xee\x01\xb2\xba\xe8\xf6y\xd96 \xdes\x10\xa2\xf9\xdb\x0cP\x1d\xda]U&!\r\xaePJC\xce'\xb6\xb5\xec\x9d~\xe0\x14q$f}\xa1d\xc2l\x02\x8d\xd7{\x8a\xa2\x9e\x9b\xc5\xb7\x89\xf1\xcc\x98\xa6\x83\xd90,\x00\x9e\xad\xa3\x17\xbf?I@"

ERR_NOSUCHSTARTUPSCRIPT = 110


def _SET_HELPER_STARTUP(origPth: str, args: dict[int, str]) -> int:
    """
    Helper function for add feature of the STARTUP function.
    > param origPth: The directory from where the interpreter is running
    > param args: Dictionary of arguments
    > return: Error code (ref. src\\errCodes.txt)
    """
    startupDir = os.path.join(origPth, "startup")
    err        = comm.ERR_SUCCESS

    for arg in args.values():
        if os.path.isfile(os.path.join(startupDir, os.path.basename(arg))):
            comm.ERR("Startup script file exists: "
                     f"\"{os.path.join(startupDir, os.path.basename(arg))}\"",
                     sl=4)
            err = err or comm.ERR_FLDIREXISTS
            continue

        try:
            sh.copy2(arg, startupDir)
        except FileNotFoundError:
            comm.ERR(f"No such file: \"{arg}\"", sl=4)
            err = err or comm.ERR_NOFL
        except PermissionError:
            comm.ERR(f"Is a directory or access is denied: \"{arg}\"", sl=4)
            err = err or comm.ERR_PERMDENIED
        except OSError:
            comm.ERR("Copy operation failed; invalid path, disc full or "
                     "unescaped characters?", sl=4)
            err = err or comm.ERR_OSERR

    return err


def _RM_HELPER_STARTUP(origPth: str, args: dict[int ,str]) -> int:
    """
    Helper function for remove feature of the STARTUP function.
    > param origPth: The directory from where the interpreter is running
    > param args: Dictionary of arguments
    > return: Error code (ref. src\\errCodes.txt)
    """
    dirList = [
        os.path.basename(i).lower()
        for i in os.scandir(os.path.join(origPth, "startup"))
    ]
    err     = comm.ERR_SUCCESS

    for arg in args.values():
        # arg is only allowed to be the filename of the startup script;
        # full paths (it doesn't even make sense!) are not allowed
        if arg.lower() in dirList:
            os.remove(os.path.join(origPth, "startup", arg))
        else:
            comm.ERR(f"No such startup script: \'{arg}\'", sl=4)
            err = err or ERR_NOSUCHSTARTUPSCRIPT

    return err


def STARTUP(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
            args: dict[int, str], opts: dict[int, str], fullComm: str,
            stream: ty.TextIO, op: str, debug: bool) -> int:
    """"
    Create a startup script.
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
    optVals    = comm.LOWERLT(opts.values())
    validOpts  = {'r', 's', 'h', "-remove", "-set", "-help"}
    remove     = False
    setStartup = False
    opAldrGiv  = False
    err        = comm.ERR_SUCCESS
    startUpDir = os.path.join(origPth, "startup")
    os.makedirs(startUpDir, exist_ok=True)

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for opt in optVals:
            if opAldrGiv:
                comm.ERR("Cannot use both -r and -s at the same time")
                return comm.ERR_INCOPTUSAGE
            if opt == 'r' or opt == "-remove":
                remove = True
            elif opt == 's' or opt == "-set":
                setStartup = True
            opAldrGiv = True

    if not args and not opts:
        available = False
        for i in os.scandir(os.path.join(origPth, "startup")):
            print(i.name)
            available = True
        if not available:
            print("No startup scripts to show")
        return err

    if not opts and args:
        if len(args) >= 2:
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT

        arg = args[sorted(args)[0]]
        try:
            with open(os.path.join(startUpDir, arg), buffering=1) as f:
                for line in f:
                    print(line, end='')
        except FileNotFoundError:
            comm.ERR(f"No such startup script: \"{os.path.join(startUpDir, arg)}\"")
            err = err or ERR_NOSUCHSTARTUPSCRIPT
        except PermissionError:
            comm.ERR(f"Is a directory or access is denied: \"{startUpDir}\"")
            err = err or comm.ERR_PERMDENIED
        except OSError:
            comm.ERR(f"Read operation failed for \"{arg}\"; invalid name "
                     "or unescaped characters?")
            err = err or comm.ERR_OSERR

        return err

    # Opt given, but no args given
    if not args:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    if remove:
        err = _RM_HELPER_STARTUP(origPth, args)
    elif setStartup:
        err = _SET_HELPER_STARTUP(origPth, args)

    return err
