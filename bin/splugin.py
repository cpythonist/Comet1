#
# Comet 1 standard library command
# Filename: bin\\splugin.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as sh
import typing as ty

srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Create a startup script.",
    "USAGE: plugin [-h] [-r script ... | -s script ...]", "ARGUMENT(S)",
    "\tscript", "\t\tComet script(s) for the plugin(s)", "OPTION(S)",
    "\t-h / --help", "\t\tDisplay help message", "\t-r / --remove",
    "\t\tRemove plugin(s)", "\t-s / --set", "\t\tAdd plugin file(s)"
)


def _SET_HELPER_PLUGIN(origPth: str, args: dict[int, str]) -> int:
    """
    Helper function for add feature of the PLUGIN function.
    > param origPth: The directory from where the interpreter is running
    > param args: Dictionary of arguments
    > return: Error code (0, 4, 5, 8) (ref. src\\errCodes.txt)
    """
    err       = 0
    pluginDir = comm.PTHJN(origPth, "plugins")

    for arg in args.values():
        if os.path.isfile(comm.PTHJN(origPth, "plugins", arg)):
            comm.ERR("Plugin file exists: "
                     f"\"{comm.PTHJN(origPth, os.path.basename(arg))}\"")
            err = err or 8
            continue

        try:
            sh.copy2(arg, pluginDir)
        except FileNotFoundError:
            comm.ERR(f"No such file: \"{arg}\"", sl=4)
            err = err or 4
        except PermissionError:
            comm.ERR(f"Is a directory or access is denied: \"{arg}\"", sl=4)
            err = err or 5

    return err


def _RM_HELPER_PLUGIN(origPth: str, args: dict[int ,str]) -> int:
    """
    Helper function for remove feature of the PLUGIN function.
    > param origPth: The directory from where the interpreter is running
    > param args: Dictionary of arguments
    > return: Error code (0, 7, 110) (ref. src\\errCodes.txt)
    Error code 110:
        No such plugin
    """
    err     = 0
    dirList = [
        os.path.basename(i).lower()
        for i in os.scandir(comm.PTHJN(origPth, "plugins"))
    ]

    for arg in args.values():
        if arg.lower() in dirList:
            os.remove(comm.PTHJN(origPth, "plugins", arg))
        else:
            comm.ERR(f"No such plugin: \'{arg}\'", sl=4)
            err = err or 110

    return err


def PLUGIN(interpreter: comet.Interpreter, command: str, args: dict[int, str],
           opts: dict[int, str], fullComm: str, stream: ty.TextIO,
           op: str) -> int:
    """"
    Create a plugin (startup) script.
    > param interpreter: Interpreter object
    > param command: Command name
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2, 7, 110) (ref. src\\errCodes.txt)
    Error code 110:
        No such plugin
    """
    optVals   = comm.lowerLT(opts.values())
    validOpts = {'r', 's', 'h', "-remove", "-set", "-help"}
    remove    = False
    setPlugin = False
    opAldrGiv = False
    err       = 0
    pluginDir = comm.PTHJN(interpreter.origPth, "plugins")
    os.makedirs(pluginDir, exist_ok=True)

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
                setPlugin = True
            opAldrGiv = True

    if not args and not opts:
        for i in os.scandir(comm.PTHJN(interpreter.origPth, "plugins")):
            print(i.name)
        return err
    
    if not opts and args:
        for arg in args.values():
            try:
                with open(pluginDir, buffering=1) as f:
                    for line in f:
                        print(line)
            except FileNotFoundError:
                comm.ERR(f"No such plugin: {pluginDir + os.sep + arg}")
                err = err or 110
        return err

    # Opt given, but no arg(s) given
    if not args:
        comm.ERR("Incorrect format")
        return 1

    if remove:
        err = _RM_HELPER_PLUGIN(interpreter.origPth, args)
    elif setPlugin:
        err = _SET_HELPER_PLUGIN(interpreter.origPth, args)

    return err
