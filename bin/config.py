#
# Comet 1 standard library command
# Filename: src\\bin\\config.py
# Copyright (c) 2025, Infinite Inc.
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
    b"x\x9cePMk\xc30\x0c=[\xbfB\xc7\r\xe6\xf4\xbe[\xd9J\xbb\xc3\xd2\xd1\xb4"
    b"\xbd\x84\x1e\xb4Yi\x0cq\x1cl\xa7c\xb0\x1f?\xdb\t\x04\xd6\x8b\x8d\xde\x87"
    b"\xf4\xa4\xb3\xe6\xef'$\xa5V\xact@\xea\x15:\xf6\xc1:\xc6\x17k8\xe0\x97\xed"
    b"\x1b}\x1d\x1d\x05m{_\x00\x9c\xaa\xf5v\xf3<\xe3X\xcb\xf6\x82\xf5\x83T\xf8"
    b"\x8bR?b=\x90#\x83EQ\\\x12\xe2q\xaao\xd4\x8d\x9c\x00\x87\x8b\x00`}\xd8\x9e"
    b"\xde7\xe5\xb1\x82\x8c\x82(\xc90\xda\x06C\xcb\x93\x90\x03;\xc8n\x10\xe7"
    b"\xdc\xe4\x8e\x85\xfd\xc7\xf1m_V\x10C\xacPJ\xc5\r\x8d]\x00q\x98\x17\x99"
    b"\x81\xc52\xc5\x01\xd9f}\xcb\xdd\x00b\x17_4\xec=]#\xa33\xa3\xfb\xc6\x82x"
    b"\xd5~\xe8\xe8\x07S\xe5L\xbe\x03\xd2\xa7\x1d\xc3\xbf\x1cq\xd9d\xf2\x1cGW"
    b"\xf1rt?\xd0e\x85cco\x9c\xf2\xa5\x7fQ\xfd\x01R(\x80\xc6"
)

ERR_NOSUCHPARAM = 122
ERR_INVPARAMNM  = 131


class Info:
    infoPROMPT = (
        "Value for the prompt of Comet.", '', "SPECIAL VALUES",
        "%c - Computer name", "%d - Date", "%e - Last error code",
        "%n - Newline (\\n)", "%o - OS name",
        "%p - Current working directory", "%s - Space", "%t - Time",
        "%u - Username", "%v - OS version", "%w - Current drive letter",
        "%0 - ANSI blink", "%1 - ANSI bold", "%2 - ANSI underline",
        "%3 - ANSI blue", "%4 - ANSI cyan", "%5 - ANSI green",
        "%6 - ANSI red", "%7 - ANSI yellow", "%8 - ANSI header",
        "%9 - ANSI reset", "%% - Percentage sign (%)"
    )

    infoPATH = (
        "The working directory of the interpreter when it starts.", '',
        "SPECIAL VALUES", "* - User directory",
        "[NONE] - Default (user directory)"
    )

    infoCDTODIRS = (
        "To change to a directory when a directory name is in place of the command."
        '', "VALID VALUES", "true/yes/on - enabled", "false/no/off - disabled"
    )

    infoEXECSCRIPTS = (
        "To execute scripts when a script name is in place of the command.",
        '', "VALID VALUES", "true/yes/on - enabled", "false/no/off - disabled"
    )

    infoTITLE = (
        "The title of the interpreter window.", '', "SPECIAL VALUES",
        "[NONE] - Default (path of the running script)"
    )

    infoINTRO = (
        "To display an introduction message when the interpreter starts.",
        '', "VALID VALUES", "true/yes/on - enabled", "false/no/off - disabled"
    )

    infoCACHE = (
        "To cache commands.", '', "VALID VALUES", "true/yes/on - enabled",
        "false/no/off - disabled"
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
        return comm.ERR_NOFL


def _def_AllParams_CONFIG_HELPER() -> int:
    """
    Helper function of CONFIG, to set all parameters to default values.
    NOTE: Please note that this function shall erase any invalid lines in the
          settings file
    > return: Error code (ref. src\\errCodes.txt)
    """
    with open(comm.SETTFL, 'w') as f:
        for defKey in comm.DFLTSETT:
            if defKey == "path":
                continue
            elif defKey == "pathSett":
                f.write(f"path={comm.DFLTSETT[defKey]}\n")
                continue
            f.write(f"{defKey}={comm.DFLTSETT[defKey]}\n")
    return comm.ERR_SUCCESS


def _def_SpecParams_CONFIG_HELPER(origPth: str, args: dict[int, str],
                                  data: dict[str, str | None]) -> int:
    """
    Helper function of CONFIG, to set specified parameters to default values.
    > param origPth: Path to the interpreter
    > param args: Dictionary of arguments supplied to the command
    > param data: Dictionary of data to be written to the settings file
    > return: Error code (ref. src\\errCodes.txt)
    """
    err = comm.ERR_SUCCESS

    for arg in args.values():
        found = False
        argL  = arg.lower()

        for key in data:
            if argL == key.lower() and arg != "path":
                if comm.DICTSRCH(key, comm.DFLTSETT, caseIn=True):
                    data[key] = comm.DFLTSETT[key.lower()]
                else:
                    data[key] = None
                found = True
            elif argL == key.lower() and arg == "path":
                data[key] = comm.DFLTSETT["pathSett"]
                found     = True

        if not found:
            if argL not in comm.KNOWNSETTPARAMS:
                comm.ERR(f"No such parameter: '{arg}'", sl=5)
                err = err or ERR_NOSUCHPARAM
            else:
                data[arg] = comm.DFLTSETT[arg.lower()]

    with open(os.path.join(origPth, "_settings.txt"), 'w') as f:
        for key in data:
            if data[key] is None:
                continue
            f.write(f"{key}={data[key]}\n")

    return comm.ERR_SUCCESS


def _rm_CONFIG_HELPER(args: dict[int, str]) -> int:
    """
    Helper function of CONFIG, to remove parameters.
    > param args: Dictionary of arguments supplied to the command
    > return: Error code (ref. src\\errCodes.txt)
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
    Helper function for CONFIG(...). Displays information on the parameters
    specified.
    > param args: Dictionary of args
    > return: Error code (ref. src\\errCodes.txt)
    """
    # TODO: COMPLETE THIS FEATURE!
    infoCls      = Info()
    recogdParams = {"prompt", "path", "title", "cdtodirs", "execscripts",
                    "intro"}
    err          = comm.ERR_SUCCESS
    argsLen      = len(args)

    if not args:
        comm.ERR("Incorrect format", sl=4)
        err = comm.ERR_INCFORMAT

    for i, arg in enumerate(args.values()):
        if arg.lower() not in data:
            comm.ERR(f"No such parameter: '{arg}'", sl=4)
            err = err or ERR_NOSUCHPARAM
        if arg.lower() not in recogdParams:
            comm.WARN(f"Unrecognised parameter: '{arg}'", sl=4)
        print(f"PARAMETER: {arg.lower()}")
        print('\n'.join(getattr(infoCls, "info" + arg.upper())).expandtabs(4))
        print() if i < argsLen - 1 else None

    return err


def CONFIG(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
           args: dict[int, str], opts: dict[int, str], fullCmd: str,
           stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    View, add/edit and restore Comet configurations.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals         = comm.LOWERLT(opts.values())
    validOpts       = {'d', 's', 'r', 'i', 'a', 'h',
                       "-default", "-set", "-remove", "-info", "-all", "-help"}
    data            = {}
    defaultParam    = False
    removeParam     = False
    setParam        = False
    infoParam       = False
    allData         = False
    optAlreadyGiven = False
    err             = comm.ERR_SUCCESS
    green           = comm.ANSIGREEN if op == '' else ''
    reset           = comm.ANSIRESET if op == '' else ''

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return comm.ERR_UNKNOPTS
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for opt in optVals:
            if optAlreadyGiven:
                comm.ERR("Operation already specified")
                return comm.ERR_INCOPTUSAGE
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
            elif opt == 'a' or opt == "-all":
                allData         = True
    
    if allData and (defaultParam or setParam or removeParam or infoParam):
        comm.ERR("Cannot use all option with other options")
        return comm.ERR_INCOPTUSAGE

    # Get all (valid) configurations
    for ln in readSett(origPth):
        attr, value = comm.GETATTRFRMSETTFL(ln)
        if attr is None or value is None:
            continue
        if not allData and attr.lower() not in comm.KNOWNSETTPARAMS:
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
            comm.ERR("Incorrect format")
            return comm.ERR_INCFORMAT
        param = args[sorted(args)[0]]
        value = args[sorted(args)[1]]
        tmp   = comm.SETSETT(param, value)
        if tmp == 2:
            comm.ERR(f"Invalid parameter name: '{param}'")
            return ERR_INVPARAMNM
        elif tmp == 5:
            comm.ERR("Access is denied")
            return comm.ERR_PERMDENIED
        return comm.ERR_SUCCESS

    # -r option
    elif removeParam:
        return _rm_CONFIG_HELPER(args)

    # -i option
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
