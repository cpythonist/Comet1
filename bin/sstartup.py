#
# Comet 1 standard library command
# Filename: src\\bin\\sstartup.py
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

helpStr = (
    "Create a startup script.", '',
    "USAGE: startup [-h] [-r script ... | -s script ...]", '', "ARGUMENTS",
    "\tscript", "\t\tStartup script", '', "OPTIONS",
    "\t-h / --help", "\t\tDisplay help message", "\t-r / --remove",
    "\t\tRemove startup script", "\t-s / --set",
    "\t\tAdd startup script file"
)


def _SET_HELPER_STARTUP(origPth: str, args: dict[int, str]) -> int:
    """
    Helper function for add feature of the STARTUP function.
    > param origPth: The directory from where the interpreter is running
    > param args: Dictionary of arguments
    > return: Error code (0, 4, 5, 6, 8) (ref. src\\errCodes.txt)
    """
    err        = 0
    startupDir = comm.PTHJN(origPth, "startup")

    for arg in args.values():
        print(origPth)
        if os.path.isfile(comm.PTHJN(startupDir, os.path.basename(arg))):
            comm.ERR("Startup script file exists: "
                     f"\"{comm.PTHJN(startupDir, os.path.basename(arg))}\"",
                     sl=4)
            err = err or 8
            continue

        try:
            sh.copy2(arg, startupDir)
        except FileNotFoundError:
            comm.ERR(f"No such file: \"{arg}\"", sl=4)
            err = err or 4
        except PermissionError:
            comm.ERR(f"Is a directory or access is denied: \"{arg}\"", sl=4)
            err = err or 5
        except OSError:
            comm.ERR("Copy operation failed; invalid path, disc full or "
                     "unescaped characters?", sl=4)
            err = err or 6

    return err


def _RM_HELPER_STARTUP(origPth: str, args: dict[int ,str]) -> int:
    """
    Helper function for remove feature of the STARTUP function.
    > param origPth: The directory from where the interpreter is running
    > param args: Dictionary of arguments
    > return: Error code (0, 7, 110) (ref. src\\errCodes.txt)
    Error code 110:
        No such startup script
    """
    err     = 0
    dirList = [
        os.path.basename(i).lower()
        for i in os.scandir(comm.PTHJN(origPth, "startup"))
    ]

    for arg in args.values():
        if arg.lower() in dirList:
            os.remove(comm.PTHJN(origPth, "startup", arg))
        else:
            comm.ERR(f"No such startup script: \'{arg}\'", sl=4)
            err = err or 110

    return err


def STARTUP(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
            args: dict[int, str], opts: dict[int, str], fullComm: str,
            stream: ty.TextIO, op: str) -> int:
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
    > return: Error code (0-2, 7, 110) (ref. src\\errCodes.txt)
    Error code 110:
        No such startup script
    """
    optVals    = comm.LOWERLT(opts.values())
    validOpts  = {'r', 's', 'h', "-remove", "-set", "-help"}
    remove     = False
    setStartup = False
    opAldrGiv  = False
    err        = 0
    startUpDir = comm.PTHJN(origPth, "startup")
    os.makedirs(startUpDir, exist_ok=True)

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opAldrGiv:
                comm.ERR("Cannot use both -r and -s at the same time")
                return 3
            if opt == 'r' or opt == "-remove":
                remove = True
            elif opt == 's' or opt == "-set":
                setStartup = True
            opAldrGiv = True

    if not args and not opts:
        available = False
        for i in os.scandir(comm.PTHJN(origPth, "startup")):
            print(i.name)
            available = True
        if not available:
            print("No startup scripts to show")
        return err

    if not opts and args:
        if len(args) >= 2:
            comm.ERR("Incorrect format")
            return 1

        arg = args[sorted(args)[0]]
        try:
            with open(comm.PTHJN(startUpDir, arg), buffering=1) as f:
                for line in f:
                    print(line, end='')
        except FileNotFoundError:
            comm.ERR(f"No such startup script: \"{comm.PTHJN(startUpDir, arg)}\"")
            err = err or 110
        except PermissionError:
            comm.ERR(f"Is a directory or access is denied: \"{startUpDir}\"")
            err = err or 5
        except OSError:
            comm.ERR(f"Read operation failed for \"{arg}\"; invalid name "
                     "or unescaped characters?")

        return err

    # Opt given, but no args given
    if not args:
        comm.ERR("Incorrect format")
        return 1

    if remove:
        err = _RM_HELPER_STARTUP(origPth, args)
    elif setStartup:
        err = _SET_HELPER_STARTUP(origPth, args)

    return err
