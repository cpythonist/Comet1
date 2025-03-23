#
# Comet 1 standard library command
# Filename: bin\\sconfig.py
# Copyright (c) 2024, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as st
import typing as ty

# Add directory "src\\core" to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "View, add/edit and restore Comet configurations.",
    "USAGE: config [-h] [-d [param ...] | -s param value | -r param ...]",
    "ARGUMENT(S)", "\tparam", "\t\tName of the parameter(s)", "\tvalue",
    "\t\tValue of the parameter", "OPTION(S)",
    "\t-d / --default", "\t\tRestore default parameter value(s)",
    "\t-h / --help", "\t\tHelp message",
    "\t-s / --set", "\t\tSet a parameter value",
    "\t-r / --remove", "\t\tRemove parameter(s)"
)


def readSett(interpreter: comet.Interpreter) -> \
        ty.Generator[str, None, int | None]:
    """
    Read settings from the settings file.
    > param interpreter: Interpreter object
    > return: Generator object yielding individual lines of the settings file
    """
    try:
        with open(os.path.join(interpreter.origPth, "_settings.txt"),
                  'r', buffering=1) as f:
            for line in f:
                yield line
    except FileNotFoundError:
        comm.ERR("\"_settings.txt\": The settings file was not found", sl=4)
        return 4


def _def_AllParams_CONFIG_HELPER() -> int:
    """
    Helper function of CONFIG, to set all parameters to default values.
    NOTE: Please note that this function shall erase any invalid lines in the 
          settings file
    > return: Error code (0) (ref. src\\errCodes.txt)
    """
    with open(comm.SETTFL, 'w') as f:
        for defKey in comm.DEFLTSETT:
            if defKey == "path":
                continue
            elif defKey == "pathSett":
                f.write(f"path={comm.DEFLTSETT[defKey]}\n")
                continue
            f.write(f"{defKey}={comm.DEFLTSETT[defKey]}\n")
    return 0


def _def_SpecParams_CONFIG_HELPER(interpreter: comet.Interpreter,
                                  args: dict[int, str], data) -> int:
    """
    Helper function of CONFIG, to set specified parameters to default values.
    > param interpreter: Interpreter object
    > param args: Dictionary of arguments supplied to the command
    > param data: Dictionary of data to be written to the settings file
    > return: Error code (0) (ref. src\\errCodes.txt)
    """
    for arg in args.values():
        found = False
        for key in data:
            if arg.lower() == key.lower() and arg != "path":
                if comm.DICTSRCH(key, comm.DEFLTSETT, caseIn=True):
                    data[key] = comm.DEFLTSETT[key.lower()]
                else:
                    data[key] = None
                found = True
            elif arg.lower() == key.lower() and arg == "path":
                data[key] = comm.DEFLTSETT["pathSett"]
                found     = True
        if not found:
            comm.ERR(f"No such parameter: '{arg}'", sl=5)

    with open(comm.PTHJN(interpreter.origPth, "_settings.txt"), 'w') as f:
        for key in data:
            if data[key] is None:
                continue
            f.write(f"{key}={data[key]}\n")

    return 0


def _rm_CONFIG_HELPER(args: dict[int, str]) -> int:
    """
    Helper function of CONFIG, to remove parameters.
    > param args: Dictionary of arguments supplied to the command
    > return: Error code (0, 1) (ref. src\\errCodes.txt)
    """
    argVals = args.values()

    if not args:
        comm.ERR("Incorrect format", sl=4)
        return 1

    st.copyfile(comm.SETTFL, comm.SETTTMP)
    with open(comm.SETTTMP, 'r') as f, open(comm.SETTFL, 'w') as g:
        for line in f:
            parts = line.partition('=')
            if parts[0].lower() not in comm.lowerLT(argVals) or parts[1] == '':
                g.write(line)

    os.remove(comm.SETTTMP)
    return 0


def CONFIG(interpreter: comet.Interpreter, command: str, args: dict[int, str],
           opts: dict[int, str], fullComm: str, stream: ty.TextIO,
           op: str) -> int:
    """
    View, add/edit and restore Comet configurations.
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-3) (ref. src\\errCodes.txt)
    """
    data: dict[str, str | None]
    optVals         = comm.lowerLT(opts.values())
    validOpts       = {'d', 's', 'r', 'h',
                       "-default", "-set", "-remove", "-help"}
    data            = {}
    defaultParam    = False
    removeParam     = False
    setParam        = False
    optAlreadyGiven = False
    err             = 0

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if optAlreadyGiven:
                comm.ERR("Operation already specified")
                return 3
            if opt == 'd' or opt == '-default':
                defaultParam    = True
                optAlreadyGiven = True
            elif opt == 's' or opt == "-set":
                setParam        = True
                optAlreadyGiven = True
            elif opt == 'r' or opt == "-remove":
                removeParam     = True
                optAlreadyGiven = True

    for lineNo, line in enumerate(readSett(interpreter)):
        attr, value = comm.GETATTRFROMSETTFL(line, lineNo)
        if isinstance(attr, int) or isinstance(value, int):
            continue
        data[attr] = value[:-1]

    # -d option
    if defaultParam:
        if args == {}:
            return _def_AllParams_CONFIG_HELPER()
        return _def_SpecParams_CONFIG_HELPER(interpreter, args, data)

    # -s option
    elif setParam:
        if len(args) != 2:
            return comm.ERR("Incorrect format")
        param = args[sorted(args)[0]]
        value = args[sorted(args)[1]]
        comm.settingsSet(interpreter.origPth, param, value)
        return 0

    # -r option
    elif removeParam:
        return _rm_CONFIG_HELPER(args)

    # Print specified parameter-value pairs
    if args != {}:
        for arg in args.values():
            if not (values := comm.DICTSRCH(arg, data, caseIn=True)):
                tmp = comm.ERR(f"'{arg}': No such parameter")
                err = err or tmp
            for value in values:
                print(f"'{repr(arg)[1:-1]}'=\"{repr(value)[1:-1]}\"")

    # Print all parameter-value pairs
    else:
        for key in data:
            print(f"'{repr(key)[1:-1]}'=\"{repr(data[key])[1:-1]}\"")

    return err
