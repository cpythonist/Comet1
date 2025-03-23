#
# Comet 1 standard library command
# Filename: bin\\salias.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import shutil as st
import typing as ty

# Add directory "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Aliases a command.",
    "USAGE: alias [-h] [[-r] name ... | [-s name command]]", "ARGUMENT(S)",
    "\tNone", "\t\tAll aliases (without options)", "\tname",
    "\t\tName(s) of the alias(es)", "\tcommand", "\t\tCommand to be aliased",
    "OPTION(S)", "\tNone", "\t\tDisplay all/specified aliases", "\t-h / --help",
    "\t\tHelp message", "\t-r", "\t\tRemove alias(es)", "\t-s",
    "\t\tSet an alias"
)


def createAlias(args: dict[int, str], command: str) -> int:
    """
    Creates an alias.
    > param args: Arguments suppiled to the command
    > param opts: Options supplied to the command
    > return: Error code (0, 5, 112) (ref. src\\errCodes.txt)
    Error code 112:
        Invalid alias name (contains illegal characters)
    """
    name    = args[sorted(args.keys())[0]]
    command = args[sorted(args.keys())[1]]
    line    = ''
    found   = False, -1

    for i, arg in enumerate(args.values()):
        if not i and not len(arg):
            continue
        if [j for j in ('=', '/', ' ', '\t', '\r', '\n') if j in arg]:
            return comm.ERR(f"Invalid alias name: '{arg}'", sl=4)

    # Try to locate alias if it already exists
    with open(aliasTxtFile, 'r', buffering=1) as f:
        for j, line in enumerate(f):
            if (line := line.strip()) == '':
                continue
            for i, char in enumerate(line):
                # '=' indicates end of alias name
                if char == '=':
                    break
            else:
                # TODO: Decide whether to warn the user
                # that an invalid line exists, or make it the job of another
                # option
                continue

            if args[sorted(args.keys())[0]].lower() == line[:i].lower():
                found = True, j
                break

    # If alias already exists, update it
    if found[0]:
        try:
            st.copyfile(aliasTxtFile, aliasTmpFile)
            with (open(aliasTmpFile, 'r', buffering=1) as f1,
                  open(aliasTxtFile, 'w', buffering=1) as f):
                for i, line in enumerate(f1):
                    if i != found[1]:
                        f.write(line)
                    else:
                        f.write("{}={}\n".format(
                            args[sorted(args.keys())[0]],
                            args[sorted(args.keys())[1]])
                        )
            os.remove(aliasTmpFile)

        except PermissionError:
            comm.ERR("Access is denied: either to delete or write to "
                     f"\"{aliasTxtFile}\" or read temporary file "
                     f"\"{aliasTmpFile}\"", sl=4)
            return 5

    # Else, create new alias (specified alias was not found in alias file)
    else:
        with open(aliasTxtFile, "a+", buffering=1) as f:
            if isinstance((prevChar := comm.RDPREVCHAR(f)), Exception):
                # Enna da inga ezutharathu
                return comm.UNERR(prevChar, str(Exception))
            f.write("{}{}={}\n".format(
                '\n' if prevChar not in ('\n', '') else '',
                name,
                command
            ))

    return 0


def getAliases(interpreter: comet.Interpreter, arg: str,
               command: str) -> int:
    """
    Gets an alias from the alias file.
    > param interpreter: Interpreter object
    > param arg: Argument(s) supplied to the command
    > param command: Command name
    > return: Error code (0, 4) (ref. src\\errCodes.txt)
    """
    with open(comm.PTHJN(interpreter.origPth, f"_aliases.txt"), 'r',
              buffering=1) as f:
        for line in f:
            if (res := extrAlias(arg, line))[0]:
                print(f"'{res[1][0]}'={res[1][1]}'")
                break
        else:
            comm.ERR(f"No such alias: '{arg}'", sl=4)
            return 4
        return 0


def removeAliases(args: dict[int, str], command: str) -> int:
    """
    Removes an alias, given the arguments supplied to the function, and the
    command name.
    > param args: The arguments supplied to the command
    > param command: The command name
    > return: Error code (0, 5, 100) (ref. src\\errCodes.txt)
    Return code 100:
        No alias to remove specified
    """
    if not args:
        comm.ERR("No alias to remove")
        return 100

    try:
        st.copyfile(aliasTxtFile, aliasTmpFile)
    except PermissionError:
        comm.ERR("Access is denied to create temporary file: "
                 f"\"{aliasTmpFile}\"")
        return 5

    try:
        with open(aliasTxtFile, 'w') as g, open(aliasTmpFile, 'r') as f:
            # TODO: Maybe can be improved by providing an error message
            # when the alias is not found.
            for line in f:
                found = False
                for arg in args.values():
                    if extrAlias(arg, line)[0]:
                        found = True
                        break
                g.write(line) if not found else None
        os.remove(aliasTmpFile)
    except FileNotFoundError:
        pass
    except PermissionError:
        comm.ERR(f"Access is denied: Alias file \"{aliasTxtFile}\" or "
                 f"temporary file \"{aliasTmpFile}\"", sl=4)
        return 5

    return 0

def rdAliases() -> int:
    """
    Read aliases from alias file.
    > param command: The alias to be fetched
    > return: Error code (0, 5, 101) (ref. src\\errCodes.txt)
    Return code 101:
        Invalid character encountered in alias file
    """
    try:
        err = 0
        with open(aliasTxtFile, 'r', buffering=1) as f:
            for i, line in enumerate(f):
                if not line.removesuffix('\n'):
                    continue
                dontPrint = False
                j         = 0
                for j, char in enumerate(line):
                    if char.isspace() or (char == '=' and not j):
                        comm.ERR(f"Invalid char: pos {j+1} in line {i+1}")
                        err       = err or 101
                        dontPrint = True
                    if char == '=':
                        break
                res = extrAlias(line[:j].strip(), line)
                print(f"'{res[1][0]}'=\"{res[1][1]}\"") if not dontPrint else None
        return err

    except PermissionError:
        comm.ERR(F"Access is denied to alias file: \"{aliasTxtFile}\"", sl=4)
        return 5


def extrAlias(word: str, line: str) \
        -> tuple[bool, str | tuple[str, str] | None]:
    """
    Check if alias name is present in a string.
    > param word: Alias to be searched for
    > param line: String to conduct the search on
    > return: True if alias name (param "word") is present in the string
              (param "line"), else False
    """
    # TODO: See if the code fails for edge cases, where the for loop will not
    # be executed even once. I have a huge suspicion it will fail in certain
    # cases...
    i     = 0
    parts = line.removesuffix('\n').partition('=')
    if parts[1] == '':
        return False, None
    if parts[0].lower() == word.lower():
        return True, (parts[0], parts[2])
    return False, ''


def ALIAS(interpreter: comet.Interpreter, command: str, args: dict[int, str],
          opts: dict[int, str], fullComm: str, stream: ty.TextIO,
          op: str) -> int:
    """
    Alias a command.
    > param interpreter: Interpreter object
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
    """
    try:
        global aliasTxtFile, aliasTmpFile
        aliasTxtFile    = os.path.join(interpreter.origPth,
                                       "_aliases.txt")
        aliasTmpFile    = os.path.join(interpreter.origPth,
                                       "bin", "_aliases.temp")
        validOpts       = {'r', 's', 'h',
                           "-remove", "-set", "-help"}
        optVals         = comm.lowerLT(opts.values())
        moreOptsAllowed = True
        rmAlias         = False
        setAlias        = False
        err             = 0

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
            return removeAliases(args, command)
        elif setAlias:
            if len(args) != 2:
                comm.ERR("Incorrect format")
                return 1
            return createAlias(args, command)

        # No arg provided: print all aliases
        if not args:
            return rdAliases()

        # 1/more args: view specified aliases
        for arg in args.values():
            tmp = getAliases(interpreter, arg, command)
            err = err or tmp
        return err

    except PermissionError:
        comm.ERR("Access is denied")
        return 5
