#
# Comet 1 standard library command
# Filename: src\\bin\\sconfig.py
# Copyright (c) 2024, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as st
import typing as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "View, add/edit and restore Comet configurations.", '',
    "USAGE: config [-h] [(-d | -i) [param ...] | -s param value | -r param ...]",
    '', "ARGUMENTS", "param", "\tName of the parameter", "value",
    "\tValue of the parameter", '', "OPTIONS",
    "-d / --default", "\tRestore default parameter value",
    "-h / --help", "\tHelp message",
    "-i / --info", "\tDisplay information about the parameter",
    "-s / --set", "\tSet a parameter value",
    "-r / --remove", "\tRemove parameter"
)


class Info:
    infoPROMPT = (
        "Value for the prompt of Comet.", "Special values:",
        "\t%c - Computer name", "\t%d - Date", "\t%e - Last error code",
        "\t%n - Newline (\\n)", "\t%o - OS name",
        "\t%p - Current working directory", "\t%s - Space", "\t%t - Time",
        "\t%u - Username", "\t%v - OS version", "\t%w - Current drive letter",
        "\t%0 - ANSI blink", "\t%1 - ANSI bold", "\t%2 - ANSI underline",
        "\t%3 - ANSI blue", "\t%4 - ANSI cyan", "\t%5 - ANSI green",
        "\t%6 - ANSI red", "\t%7 - ANSI yellow", "\t%8 - ANSI header",
        "\t%9 - ANSI reset", "\t%% - Percentage sign (%)"
    )


def readSett(origPth: str) -> ty.Generator[str, None, int | None]:
    """
    Read settings from the settings file.
    > param origPth: Path to the interpreter
    > return: Generator object yielding individual lines of the settings file
    """
    try:
        with open(os.path.join(origPth, "_settings.txt"),
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
        for defKey in comm.DFLTSETT:
            if defKey == "path":
                continue
            elif defKey == "pathSett":
                f.write(f"path={comm.DFLTSETT[defKey]}\n")
                continue
            f.write(f"{defKey}={comm.DFLTSETT[defKey]}\n")
    return 0


def _def_SpecParams_CONFIG_HELPER(origPth: str, args: dict[int, str],
                                  data: dict[str, str | None]) -> int:
    """
    Helper function of CONFIG, to set specified parameters to default values.
    > param origPth: Path to the interpreter
    > param args: Dictionary of arguments supplied to the command
    > param data: Dictionary of data to be written to the settings file
    > return: Error code (0) (ref. src\\errCodes.txt)
    """
    for arg in args.values():
        found = False
        for key in data:
            if arg.lower() == key.lower() and arg != "path":
                if comm.DICTSRCH(key, comm.DFLTSETT, caseIn=True):
                    data[key] = comm.DFLTSETT[key.lower()]
                else:
                    data[key] = None
                found = True
            elif arg.lower() == key.lower() and arg == "path":
                data[key] = comm.DFLTSETT["pathSett"]
                found     = True
        if not found:
            comm.ERR(f"No such parameter: '{arg}'", sl=5)

    with open(comm.PTHJN(origPth, "_settings.txt"), 'w') as f:
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
            if parts[0].lower() not in comm.LOWERLT(argVals) or parts[1] == '':
                g.write(line)

    os.remove(comm.SETTTMP)
    return 0


def _info_CONFIG_HELPER(args: dict[int, str], data: dict[str, str | None]) \
        -> int:
    """
    Helper function for CONFIG(). Displays information on the parameters
    specified.
    > param args: Dictionary of args
    > return: Error code () (ref. src\\errCodes.txt)
    """
    # TODO: COMPLETE THIS FEATURE!
    infoCls      = Info()
    recogdParams = {"prompt", "path", "title", "cdtodirs", "execscripts",
                    "intro"}
    err          = 0

    for arg in args.values():
        if arg.lower() not in data:
            comm.ERR(f"No such parameter: '{arg}'", sl=4)
            err = err or 122
        if arg.lower() not in recogdParams:
            comm.WARN(f"Unrecognised parameter: '{arg}'", sl=4)
        print('\n'.join(getattr(infoCls, "info" + arg.upper())).expandtabs(4))

    return err


def CONFIG(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
           args: dict[int, str], opts: dict[int, str], fullComm: str,
           stream: ty.TextIO, op: str) -> int:
    """
    View, add/edit and restore Comet configurations.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-3, 5) (ref. src\\errCodes.txt)
    """
    data: dict[str, str | None]
    optVals         = comm.LOWERLT(opts.values())
    validOpts       = {'d', 's', 'r', 'i', 'h',
                       "-default", "-set", "-remove", "-info", "-help"}
    data            = {}
    defaultParam    = False
    removeParam     = False
    setParam        = False
    infoParam       = False
    optAlreadyGiven = False
    err             = 0
    green           = comm.ANSIGREEN if op == '' else ''
    reset           = comm.ANSIRESET if op == '' else ''

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
            elif opt == 'i' or opt == "-info":
                infoParam       = True
                optAlreadyGiven = True

    for lnNo, ln in enumerate(readSett(origPth)):
        attr, value = comm.GETATTRFRMSETTFL(ln, lnNo)
        if isinstance(attr, int) or isinstance(value, int):
            continue
        data[attr] = value[:-1]

    # -d option
    if defaultParam:
        if args == {}:
            return _def_AllParams_CONFIG_HELPER()
        return _def_SpecParams_CONFIG_HELPER(origPth, args, data)

    # -s option
    elif setParam:
        if len(args) != 2:
            return comm.ERR("Incorrect format")
        param = args[sorted(args)[0]]
        value = args[sorted(args)[1]]
        tmp   = comm.SETSETT(param, value)
        if tmp == 2:
            comm.ERR(f"Invalid parameter name: '{param}'")
        elif tmp == 5:
            comm.ERR("Access is denied")
        return tmp

    # -r option
    elif removeParam:
        return _rm_CONFIG_HELPER(args)

    elif infoParam:
        return _info_CONFIG_HELPER(args, data)

    # Print specified parameter-value pairs
    if args != {}:
        for arg in args.values():
            if (not (values := comm.DICTSRCH(arg, data, caseIn=True))
                or values is None):
                tmp = comm.ERR(f"No such parameter: '{arg}'")
                err = err or tmp
                continue
            for value in values:
                if not comm.PARAMOK(arg):
                    continue
                print(f"{green + repr(arg)[1:-1] + reset}"
                      f"='{repr(value)[1:-1]}'")

    # Print all parameter-value pairs
    else:
        for key in data:
            if not comm.PARAMOK(key):
                continue
            print(f"{green + repr(key)[1:-1] + reset}"
                  f"='{repr(data[key])[1:-1]}'")

    return err
