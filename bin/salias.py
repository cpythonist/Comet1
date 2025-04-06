#
# Comet 1 standard library command
# Filename: src\\bin\\salias.py
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
    "Aliases a command.", '',
    "USAGE: alias [-h] [[-r] name ... | [-s name command]]", '', "ARGUMENTS",
    "None", "\tAll aliases (without options)", "name",
    "\tName of the alias", "command", "\tCommand to be aliased", '',
    "OPTIONS", "None", "\tDisplay all/specified aliases", "-h / --help",
    "\tHelp message", "-r", "\tRemove alias", "-s",
    "\tSet an alias"
)


def createAlias(aliasTxtFl: str, aliasTmpFl: str, args: dict[int, str],
                command: str) -> int:
    """
    Creates an alias.
    > param aliasTxtFl: Path of alias file
    > param aliasTmpFl: Path of temporary alias file
    > param args: Arguments suppiled to the command
    > param opts: Options supplied to the command
    > return: Error code (0, 5, 112) (ref. src\\errCodes.txt)
    Error code 112:
        Invalid alias name (contains illegal characters)
    """

    # One of the most inefficient pieces of code I have ever written. Don't
    # know how to make it better.

    name    = args[sorted(args)[0]]
    command = args[sorted(args)[1]]
    line    = ''
    found   = False, -1

    for i, arg in enumerate(args.values()):
        if not i and not len(arg):
            continue
        if not comm.PARAMOK(arg):
            return comm.ERR(f"Invalid alias name: '{arg}'", sl=4)

    # Try to locate alias if it already exists
    with open(aliasTxtFl, 'r', buffering=1) as f:
        for j, line in enumerate(f):
            if line.isspace() or line == '':
                continue

            parts = line.removesuffix('\n').partition('=')
            if not comm.PARAMOK(parts[0]):
                comm.WARN(f"Invalid alias name in alias file: '{parts[0]}'",
                          sl=4)
                continue

            if name.lower() == parts[0].lower():
                found = True, j
                break

    # If alias already exists, update it
    if found[0]:
        try:
            st.copyfile(aliasTxtFl, aliasTmpFl)
            with (open(aliasTmpFl, 'r', buffering=1) as f1,
                  open(aliasTxtFl, 'w', buffering=1) as f):
                for i, line in enumerate(f1):
                    if i != found[1]:
                        f.write(line)
                    else:
                        f.write(f"{name}={command}\n")
            os.remove(aliasTmpFl)

        except PermissionError:
            comm.ERR(f"Access is denied to modify \"{aliasTxtFl}\" or read "
                     f"temporary file \"{aliasTmpFl}\"", sl=4)
            return 5

    # Else, create new alias (specified alias was not found in alias file)
    else:
        with open(aliasTxtFl, "a+", buffering=1) as f:
            if isinstance((prevChar := comm.RDPREVCHAR(f)), Exception):
                # Enna da inga ezutharathu
                return comm.UNERR(prevChar, str(Exception))
            f.write("{}{}={}\n".format(
                '\n' if prevChar not in ('\n', '') else '',
                name,
                command
            ))

    return 0


def getAliases(aliasFl: str, args: dict[int, str]) -> int:
    """
    Gets an alias from the alias file.
    > param aliasFl: Path of alias file
    > param arg: Argument(s) supplied to the command
    > return: Error code (0, 4) (ref. src\\errCodes.txt)
    """
    with open(aliasFl, 'r', buffering=1) as f:
        for i, line in enumerate(f):
            if not line or line.isspace():
                continue

            for arg in args.values():
                res = extrAlias(arg, line)
                if isinstance(res, tuple):
                    print(f"'{res[0]}'={res[1]}'")
                    break
                elif res == '':
                    continue
                elif res == "invName":
                    comm.WARN(f"Invalid alias name: '{arg}'", sl=4)
                elif res == "invLn":
                    comm.WARN(f"Invalid alias line at line {i + 1}", sl=4)

    return 0


def rmAliases(aliasTxtFl: str, aliasTmpFl: str, args: dict[int, str]) -> int:
    """
    Removes an alias, given the arguments supplied to the function, and the
    command name.
    > param aliasTxtFl: Path of alias file
    > param aliasTmpFl: Path of temporary alias file
    > param args: The arguments supplied to the command
    > return: Error code (0, 5, 100) (ref. src\\errCodes.txt)
    Return code 100:
        No alias to remove specified
    Return code 119:
        extrAlias() returned 'what?', which is not supposed to happen
    """
    err = 0

    if not args:
        # Don't think this is ever going to execute :)
        comm.ERR("What do you want to remove? Your head?", sl=4)
        return 100

    try:
        st.copyfile(aliasTxtFl, aliasTmpFl)
    except PermissionError:
        comm.ERR(f"Access is denied: {aliasTmpFl}", sl=4)
        return 5

    try:
        with open(aliasTxtFl, 'w') as g, open(aliasTmpFl, 'r') as f:
            # TODO: Maybe can be improved by providing an error message
            # when the alias is not found.
            for i, line in enumerate(f):
                if not line or line.isspace():
                    continue

                found = False
                for arg in args.values():
                    res = extrAlias(arg, line)
                    if isinstance(res, tuple):
                        found = True
                        break
                    elif res == '':
                        continue
                    elif res == "invName":
                        comm.WARN(f"Invalid alias name: '{arg}'", sl=4)
                    elif res == "invLn":
                        comm.WARN(f"Invalid alias at line {i + 1}", sl=4)

                g.write(line) if not found else None

        os.remove(aliasTmpFl)

    except FileNotFoundError:
        pass

    except PermissionError:
        comm.ERR(f"Access is denied: Alias file \"{aliasTxtFl}\" or "
                 f"temporary file \"{aliasTmpFl}\"", sl=4)
        return 5

    return 0

def rdAliases(aliasTxtFl: str) -> tuple[list[tuple[str, str]], int]:
    """
    Read aliases from alias file.
    > param aliasTxtFl: Path of alias file
    > return: Error code (0, 5, 120) (ref. src\\errCodes.txt)
    Error code 120:
        No alias file found
    """
    try:
        allAliases = []

        with open(aliasTxtFl, 'r', buffering=1) as f:
            for i, line in enumerate(f):
                if not line.removesuffix('\n'):
                    continue

                parts = line.partition('=')
                res   = extrAlias(parts[0], line)

                if isinstance(res, tuple):
                    allAliases.append(res)
                    continue
                elif res == '':
                    continue
                elif res == "emptyLn":
                    pass
                elif res == "invLn":
                    comm.WARN(f"Invalid alias line at line {i + 1}", sl=4)
                elif res == "invName":
                    comm.WARN(f"Invalid alias name at line {i + 1}: '{parts[0]}'",
                              sl=4)

        return allAliases, 0

    except FileNotFoundError:
        comm.ERR("No alias file found", sl=4)
        return [], 120

    except PermissionError:
        comm.ERR(F"Access is denied to alias file: {aliasTxtFl}", sl=4)
        return [], 5


def extrAlias(word: str, line: str) \
        -> tuple[str, str] | str:
    """
    Check if alias name is present in a string.
    > param word: Alias to be searched for
    > param line: String to conduct the search on
    > return: True if alias name (param "word") is present in the string
              (param "line"), else False
    """
    if line == '' or line.isspace():
        return "emptyLn"
    parts = line.removesuffix('\n').partition('=')
    if parts[1] == '':
        return "invLn"
    if not comm.PARAMOK(parts[0]):
        return "invName"
    if parts[0].lower() == word.lower():
        return parts[0], parts[2]
    return ''


def ALIAS(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
          args: dict[int, str], opts: dict[int, str], fullComm: str,
          stream: ty.TextIO, op: str) -> int:
    """
    Alias a command.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Command name
    > param args: Arguments supplied to the command
    > param opts: Options supplied to the command
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-3, 5, 100, 101, 112) (ref. src\\errCodes.txt)
    Return code 100:
        No alias to remove specified
    Return code 101:
        Invalid character encountered in alias file
    Return code 112:
        Invalid alias name (contains illegal characters)
    Return code 121:
        No such alias
    """
    try:
        global green, reset
        aliasTxtFl      = comm.PTHJN(origPth, "_aliases.txt")
        aliasTmpFl      = comm.PTHJN(origPth, "bin", "_aliases.temp")
        validOpts       = {'r', 's', 'h',
                           "-remove", "-set", "-help"}
        optVals         = comm.LOWERLT(opts.values())
        moreOptsAllowed = True
        rmAlias         = False
        setAlias        = False
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
                if not moreOptsAllowed:
                    comm.ERR("Incompatible options used together: "
                             f"{comm.OPTSJOIN(opts)}")
                    return 3
                if opt == 'r' or opt == "-remove":
                    rmAlias = True
                elif opt == 's' or opt == "-set":
                    setAlias = True
                moreOptsAllowed = False

        if rmAlias:
            if not args:
                comm.ERR("Incorrect format")
                return 1
            return rmAliases(aliasTxtFl, aliasTmpFl, args)
        elif setAlias:
            if len(args) != 2:
                print(len(args), args)
                comm.ERR("Incorrect format")
                return 1
            return createAlias(aliasTxtFl, aliasTmpFl, args, command)

        allAliases = rdAliases(aliasTxtFl)
        if allAliases[1] != 0:
            return allAliases[1]

        # No arg: print all aliases
        if not args:
            print(
                *(f"{green}{alias[0]}{reset}='{alias[1]}'"
                  for alias in allAliases[0]),
                sep='\n'
            )
            return 0

        # 1/more args: view specified aliases
        err = 0
        for arg in args.values():
            found = False
            for alias in allAliases[0]:
                if alias[0].lower() != arg.lower():
                    continue
                print(f"{green}{alias[0]}{reset}={alias[1]}")
                found = True
                break
            if not found:
                comm.ERR(f"No such alias: '{arg}'")
                err = err or 121

        return err

    except PermissionError:
        comm.ERR("Access is denied")
        return 5
