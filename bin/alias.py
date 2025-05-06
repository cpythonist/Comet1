#
# Comet 1 standard library command
# Filename: src\\bin\\alias.py
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
    b"x\x9c5\x8f=\x8f\xc20\x0c\x86\xe7\xf8Wx\xbc\x1bR\xf6\xdb\xaa\x03\xc1\rW"
    b"\x10\x85\xa9\xea\x10\xa8K\"\xe5\xa3\xaa\x03\xe8\xa4\xfb\xf1\xa4MY\xfc\xf5"
    b"\xd8\xaf\xed\xd2\x1a\xc5x\r\xce)\xdfq\x01p\xae\xcb\xed\xe6\x0b\xd5\\o\xa4"
    b"n\xb1i\xe4\xd8\xa2W\x8e\xb0(\n\xfcOU\xce\xe92\xd6\xb6\x00\xe5q{\xfe\xddT"
    b"\xa7\x1a\xaa\xe0\tDim\xd6 \xc6\x8f\xa7\x89:\xdc#\x86!\x9a\xe0\xf9\x13\xa6"
    b"i\x10\xd5\xa4\x11z\x8c\x9ar/,\x82 \xbes\x801\xe0e\x81\xd4\x01\xec\x0f\xa7"
    b"\x9f}\xf5\xde\xb16<X\xf5\x97\xb0]\xf1@W\xd3\x1b\xea\xde[Aj\\\xa1\x94\x9a"
    b"\xec\x00b\x97,:bV7\x029\xced$\x17\x1eI\xe68\xfb\xe5\x82\xf4\xda\xc4\x98\""
    b"\x88\x9a\"*\x9f\xc1\x0b\xeb\xd9^Z"
)

ERR_NOALIASTORM     = 100
ERR_INVCHRINALIASFL = 101
ERR_INVALIASNM      = 112
ERR_NOALIASFL       = 120
ERR_NOSUCHALIAS     = 121


def createAlias(aliasTxtFl: str, aliasTmpFl: str, args: dict[int, str],
                cmd: str) -> int:
    """
    Creates an alias.
    > param aliasTxtFl: Path of alias file
    > param aliasTmpFl: Path of temporary alias file
    > param args: Arguments suppiled to the command
    > param opts: Options supplied to the command
    > return: Error code (ref. src\\errCodes.txt)
    """

    # One of the most inefficient pieces of code I have ever written. Don't
    # know how to make it better.

    nm    = args[sorted(args)[0]]
    cmd   = args[sorted(args)[1]]
    ln    = ''
    found = False, -1

    if not comm.PARAMOK(nm):
        comm.ERR(f"Invalid alias name: '{nm}'", sl=4)
        return ERR_INVALIASNM

    # Try to locate alias if it already exists
    with open(aliasTxtFl, 'r', buffering=1) as f:
        for j, ln in enumerate(f):
            if ln.isspace() or ln == '':
                continue

            parts = ln.removesuffix('\n').partition('=')
            if not comm.PARAMOK(parts[0]):
                comm.WARN(f"Invalid alias name in alias file: '{parts[0]}'",
                          sl=4)
                continue

            if nm.lower() == parts[0].lower():
                found = True, j
                break

    # If alias already exists, update it
    if found[0]:
        try:
            st.copyfile(aliasTxtFl, aliasTmpFl)

            with (open(aliasTmpFl, 'r', buffering=1) as g,
                  open(aliasTxtFl, 'w', buffering=1) as f):
                for i, ln in enumerate(g):
                    if i != found[1]:
                        f.write(ln)
                    else:
                        f.write(f"{nm}={cmd}\n")

            os.remove(aliasTmpFl)

        except PermissionError:
            comm.ERR(f"Access is denied either to modify \"{aliasTxtFl}\" or read temporary file \"{aliasTmpFl}\"",
                     sl=4)
            return comm.ERR_PERMDENIED

    # Else, create new alias (specified alias was not found in alias file)
    else:
        with open(aliasTxtFl, "a+", buffering=1) as f:
            if isinstance((prevChar := comm.RDPREVCHAR(f)), Exception):
                # Enna da inga ezutharathu
                comm.UNERR(prevChar, str(Exception))
                return comm.ERR_UNKNOWN
            f.write("{}{}={}\n".format(
                '\n' if prevChar not in ('\n', '') else '',
                nm,
                cmd
            ))

    return comm.ERR_SUCCESS


def getAliases(aliasFl: str, args: dict[int, str]) -> int:
    """
    Gets an alias from the alias file.
    > param aliasFl: Path of alias file
    > param arg: Argument(s) supplied to the command
    > return: Error code (ref. src\\errCodes.txt)
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
                    comm.WARN(f"Cannot parse line {i + 1} in alias file", sl=4)

    return comm.ERR_SUCCESS


def rmAliases(aliasTxtFl: str, aliasTmpFl: str, args: dict[int, str]) -> int:
    """
    Removes an alias, given the arguments supplied to the function, and the
    command name.
    > param aliasTxtFl: Path of alias file
    > param aliasTmpFl: Path of temporary alias file
    > param args: The arguments supplied to the command
    > return: Error code (ref. src\\errCodes.txt)
    """
    if not args:
        # Don't think this is ever going to execute :)
        comm.ERR("What do you want to remove? Your head?", sl=4)
        return ERR_NOALIASTORM

    try:
        st.copyfile(aliasTxtFl, aliasTmpFl)
    except PermissionError:
        comm.ERR(f"Access is denied: {aliasTmpFl}", sl=4)
        return comm.ERR_PERMDENIED

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
        return comm.ERR_PERMDENIED

    return comm.ERR_SUCCESS

def rdAliases(aliasTxtFl: str) -> tuple[list[tuple[str, str]], int]:
    """
    Read aliases from alias file.
    > param aliasTxtFl: Path of alias file
    > return: Error code (ref. src\\errCodes.txt)
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

        return allAliases, comm.ERR_SUCCESS

    except FileNotFoundError:
        comm.ERR("No alias file found", sl=4)
        return [], ERR_NOALIASFL

    except PermissionError:
        comm.ERR(F"Access is denied to alias file: {aliasTxtFl}", sl=4)
        return [], comm.ERR_PERMDENIED


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


def ALIAS(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
          args: dict[int, str], opts: dict[int, str], fullCmd: str,
          stream: ty.TextIO, op: str, debug: bool) -> int:
    """
    Alias commands.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Command name
    > param args: Arguments supplied to the command
    > param opts: Options supplied to the command
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    try:
        aliasTxtFl      = os.path.join(origPth, "_aliases.txt")
        aliasTmpFl      = os.path.join(origPth, "bin", "_aliases.tmp")
        validOpts       = {'r', 's', 'h',
                           "-remove", "-set", "-help"}
        optVals         = comm.LOWERLT(opts.values())
        moreOptsAllowed = True
        rmAlias         = False
        setAlias        = False
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
                if not moreOptsAllowed:
                    comm.ERR("Incompatible options used together: "
                             f"{comm.OPTSJOIN(opts)}")
                    return comm.ERR_INCOPTUSAGE
                if opt == 'r' or opt == "-remove":
                    rmAlias = True
                elif opt == 's' or opt == "-set":
                    setAlias = True
                moreOptsAllowed = False

        if rmAlias:
            if not args:
                comm.ERR("Incorrect format")
                return comm.ERR_INCFORMAT
            return rmAliases(aliasTxtFl, aliasTmpFl, args)
        elif setAlias:
            if len(args) != 2:
                print(len(args), args)
                comm.ERR("Incorrect format")
                return comm.ERR_INCFORMAT
            return createAlias(aliasTxtFl, aliasTmpFl, args, cmd)

        allAliases = rdAliases(aliasTxtFl)
        if allAliases[1] != 0:
            return allAliases[1]

        # No arg: print all aliases
        if not args:
            if allAliases[0]:
                print(
                    *(f"{green}{alias[0]}{reset}='{alias[1]}'"
                    for alias in allAliases[0]),
                    sep='\n'
                )
            return comm.ERR_SUCCESS

        # 1/more args: view specified aliases
        err = comm.ERR_SUCCESS
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
                err = err or ERR_NOSUCHALIAS

        return err

    except PermissionError:
        comm.ERR("Access is denied")
        return comm.ERR_PERMDENIED
