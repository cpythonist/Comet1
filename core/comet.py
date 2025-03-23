#
# Comet 1 source code
# Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename        : src\\core\\comet.py
# File description: Contains the Comet interpreter, the parser, and the
#                   built-in commands
#

import io
import os
import sys
import contextlib     as cl
import ctypes         as ct
import datetime       as dt
import importlib      as il
import importlib.util as ilu
import msvcrt         as ms
import pathlib        as pl
import subprocess     as sp
import timeit         as ti
import typing         as ty
import commons        as comm


class Parser:
    """
    # TODO: Complete this comment!
    & - AND
    ^ - OR
    | - PIPE
    ; - SEPARATOR
    > - REDIRECTION
    < - (?)
    """
    def __init__(self) -> None:
        self.src      = ''
        self.char     = ''
        self.pastChar = ''
        self.pos      = -1
        self.spChars  = {
            '&': 100,
            '^': 101,
            '|': 102,
            ';': 103,
            '>': 104,
            '<': 105
        }
        self.escChars = {
            "\\\\": '\\',
            "\\\"": '"',
            "\\'" : '\'',
            "\\n" : '\n',
        }
        self._rdChar()

    def _rdChar(self) -> None:
        if self.pos < len(self.src)-1:
            self.pos      += 1
            self.pastChar  = self.char
            self.char      = self.src[self.pos]
        else:
            self.char = '\0'

    def _pkChar(self) -> str:
        if self.pos < len(self.src)-1:
            return self.src[self.pos+1]
        return '\0'

    def _rdUnquotedArg(self, varTable: dict[str, str]) -> str:
        startPos = self.pos
        while not self.char.isspace() and self.char not in self.spChars:
            if self.char == '\0':
                return self.src[startPos:self.pos+1]
            # For escape characters
            if self.char == '\\' and self.pos < len(self.src)-1:
                self._rdChar()
                if self.char == '\\':
                    self.src = self.src[:self.pos-1] + '\\' + self.src[self.pos+1:]
                elif self.char == 'n':
                    self.src = self.src[:self.pos-1] + '\n' + self.src[self.pos+1:]
                elif self.char == '"':
                    self.src = self.src[:self.pos-1] + '"' + self.src[self.pos+1:]
                elif self.char == '\'':
                    self.src = self.src[:self.pos-1] + '\'' + self.src[self.pos+1:]
                # self._rdChar()
            self._rdChar()
        return self.src[startPos:self.pos]

    def _rdQuotedCommOrArg(self, quote: str, varTable: dict[str, str]) -> str:
        startPos = self.pos
        self._rdChar()
        while self.char != quote:
            if self.char == '\0':
                return self.src[startPos+1:self.pos+1]

            # if self.char == '$':
            #     if self.pos < len(self.src) - 1:
            #         if self.src[self.pos+1] == '$':
            #             self.src = self.src[:self.pos+1] + self.src[self.pos+2:]
            #             self._rdChar()
            #         else:
            #             if self.src[self.pos+1] == '(':
            #                 startPosTmp = self.pos
            #                 while self.char != ')':
            #                     if self._pkChar() == '\0':
            #                         return self.src[startPos+1:self.pos+1]
            #                     self._rdChar()
            #                 self.src = self.src[:self.pos] + str()

            # For escape characters
            if self.char == '\\' and self.pos < len(self.src)-1:
                self._rdChar()
                if self.char == '\\':
                    self.src = self.src[:self.pos-1] + '\\' + self.src[self.pos+1:]
                elif self.char == 'n':
                    self.src = self.src[:self.pos-1] + '\n' + self.src[self.pos+1:]
                elif self.char == '"':
                    self.src = self.src[:self.pos-1] + '"' + self.src[self.pos+1:]
                elif self.char == '\'':
                    self.src = self.src[:self.pos-1] + '\'' + self.src[self.pos+1:]
                # self._rdChar()
            self._rdChar()

        return self.src[startPos+1:self.pos]

    def _rdOpt(self) -> str:
        stPos = self.pos
        self._rdChar()
        while not self.char.isspace() and self.char not in self.spChars:
            if self.char == '\0':
                return self.src[stPos+1:self.pos+1]
            self._rdChar()
        return self.src[stPos+1:self.pos]

    def _rdComm(self) -> str:
        startPos = self.pos
        # Quoted command/file
        if (quote := self.char == '"') or self.char == '\'':
            tmp = self._rdQuotedCommOrArg('"' if quote else '\'')
            self._rdChar()
            return tmp
        self._rdChar()
        while not self.char.isspace() and self.char not in self.spChars:
            if self.char == '\0':
                return self.src[startPos:self.pos+1]
            self._rdChar()
        return self.src[startPos:self.pos]

    def parse(self, varTable: dict[str, str]) \
            -> list[tuple[str, dict[int, str], dict[int, str]] | str]:
        """
        Parse the source string present in self.src.
        > param varTable: Variable table
        > return: List of tuple of command, arguments, options, separated by
                  strings representing various operations
        """
        args: dict[int, str]
        opts: dict[int, str]
        full: list[tuple[str, dict[int, str], dict[int, str]] | str]
        self.src  = self.src.strip()
        command   = ''
        args      = {}
        opts      = {}
        full      = []
        count     = 0
        self.char = ''
        self.pos  = -1
        self._rdChar()

        command = self._rdComm()

        while self.char != '\0':
            if self.char.isspace():
                self._rdChar()
                continue

            if self.char in self.spChars:
                self.src  = self.src[self.pos+1:]
                full     += [(command, args, opts), self.char,
                             *self.parse(varTable)]
                return full

            elif (temp := (self.char == '\'')) or self.char ==  '"':
                arg         = self._rdQuotedCommOrArg('\'' if temp else '"',
                                                      varTable)
                args[count] = arg

            elif self.char == '-' and not self._pkChar().isspace() \
                    and self._pkChar() != '\0':
                opt         = self._rdOpt()
                opts[count] = opt

            elif self.char != ' ':
                arg         = self._rdUnquotedArg(varTable)
                args[count] = arg

            count += 1
            self._rdChar()

        full.append((command, args, opts))
        return full


class BuiltInComms:
    """
    The command functions have the following parameters:
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Arguments of the command
    > param opts: Options of the command
    > param fullComm: Full prompt line
    > param stream: Original stdout
    > return: Error code (ref. src\\errCodes.txt)
    """
    def __init__(self, mainFlTitle: str) -> None:
        self.mainFlTitle   = mainFlTitle
        # I'm sorry.
        self.helpABIRAM    = ("Prints out a fact.", "USAGE: abiram [-h]",
                              "OPTION(S)", "\t-h / --help", "\t\tHelp message")
        self.helpABOUT     = ("Displays information about Comet.",
                              "USAGE: about [-h]",
                              "OPTION(S)", "\t-h / --help", "\t\tHelp message")
        self.helpAMIT      = (
            "Mocks Amit.", "USAGE: amit [-h] [msg ...]", "ARGUMENT(S)",
            "\tNONE", "\t\tPrints the default output", "\tmsg",
            "\t\tCustom message(s)", "OPTION(S)", "\t-h / --help",
            "\t\tHelp message"
        )
        self.helpCD        = (
            "Changes the current working directory.", "USAGE: cd [-h] [path]",
            "ARGUMENT(S):", "\tNone", "\t\tPrints current working directory",
            "\tpath", "\t\tDirectory to change to", "\t\tSpecial symbols:",
            "\t\t*: User directory", "\t\t<: Previous working directory",
            "\t\t?: Print current working directory",
            "\t\t\\ or /: Root directory for current drive",
            "OPTION(S)", "\t-h / --help", "\t\tHelp message"
        )
        self.helpCLEAR     = ("Clears the output screen.", "USAGE: clear [-h]",
                              "OPTION(S)", "\t-h / --help", "\t\tHelp message")
        self.helpCOMET     = ("Displays information on the Comet interpreter.",
                              "USAGE: comet [-h]", "OPTION(S)", "\t-h / --help",
                              "\t\tHelp message")
        self.helpCOMMAND   = (
            "Run terminal commands.", "USAGE: command [-h] comm",
            "ARGUMENT(S)", "\tcomm", "\t\tCommand to be executed in terminal",
            "OPTION(S)", "\t-h / --help", "\t\tHelp message"
        )
        self.helpDATE      = ("Displays the current system date.",
                              "USAGE: date [-h]", "OPTION(S)", "\t-h / --help",
                              "\t\tHelp message")
        self.helpCREDITS   = ("Displays credits.", "USAGE: credits [-h]")
        self.helpEXIT      = ("Exits the program.", "USAGE: exit [-h]",
                              "OPTION(S)", "\t-h / --help", "\t\tHelp message")
        self.helpGET       = (
            "Gets an interpreter variable's value.", "USAGE: get [-h] [var]",
            "ARGUMENT(S)", "\tvar", "\t\tVariable to be accessed", "OPTION(S)",
            "\t-h / --help", "\t\tHelp message"
        )
        self.helpHELP      = (
            "Displays the help menu.", "USAGE: help [-h] [command ...]",
            "ARGUMENT(S)", "\tcommand", "\t\tCommand(s) to display help for",
            "OPTION(S)", "\t-h / --help", "\t\tHelp message"
        )
        self.helpINTRO     = ("Displays the startup string.",
                              "USAGE: intro [-h]", "OPTION(S)",
                              "\t-h / --help", "\t\tHelp message")
        self.helpQUIT      = ("Exits the program.", "USAGE: quit [-h]")
        self.helpRUNPATH   = ("Print the path from where the interpreter is "
                              "running.", "USAGE: runpath [-h]", "OPTION(S)",
                              "\t-h / --help", "\t\tHelp message")
        self.helpSET       = (
            "Sets interpreter variables.",
            "USAGE: set [-h] (name value | -r name ...)", "ARGUMENT(S)",
            "\tname", "\t\tName(s) of the variable(s)", "\tvalue",
            "\t\tValue of the variable", "OPTION(S)", "\tNone",
            "\t\tSet an interpreter variable", "\t-h / --help",
            "\t\tHelp message", "\t-r", "\t\tDelete an interpreter variable"
        )
        self.helpSTOP      = (
            "Pauses the program and waits for user to press any key.",
            "USAGE: stop [-h]", "OPTION(S)", "\t-h / --help",
            "\t\tHelp message"
        )
        self.helpTIME      = ("Displays the current system time.",
                              "USAGE: time [-h]", "OPTION(S)",
                              "\t-h / --help", "\t\tHelp message")
        self.helpTIMEIT    = (
            "Time the execution of a command.", "USAGE: timeit line",
            "ARGUMENT(S)", "\tline", "\t\tCommand to be executed",
            "Please note that -h / --help option is unavailable for the "
                "timeit command due to complications with parsing.",
            "Use \"help timeit\" for its help text."
        )
        self.helpTITLE     = (
            "Changes the title of the console window.",
            "USAGE: title [-h] [str]", "ARGUMENT(S)", "\tNONE",
            "\t\tRevert to original title", "\tstr",
            "\t\tNew title of the console window", "OPTION(S)",
            "\t-h / --help", "\t\tHelp message"
        )
        self.helpVER       = ("Displays the version of Comet interpreter.",
                              "USAGE: ver [-h]", "OPTION(S)", "\t-h / --help",
                              "\t\tHelp message")
        self.helpWHEREIS   = (
            "Displays the location of a command.",
            "USAGE: whereis [-h] command ...", "ARGUMENT(S)", "\tcommand",
            "\t\tName of the command", "OPTION(S)", "\t-h / --help",
            "\t\tDisplay help message"
        )

    def ABIRAM(self, interpreter: "Interpreter", command: str,
              args: dict[int, str], opts: dict[int, str], fullComm: str,
              stream: ty.TextIO, op: str) -> int:
        """
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpABIRAM))
                return 0
        if args:
            comm.ERR("Incorrect format")
            return 1
        print("ABIRAM is GAY!")
        return 0

    def ABOUT(self, interpreter: "Interpreter", command: str,
              args: dict[int, str], opts: dict[int, str], fullComm: str,
              stream: ty.TextIO, op: str) -> int:
        """
        Displays the "about" of Comet.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpABOUT))
                return 0
        if args:
            comm.ERR("Incorrect format")
            return 1
        print("Comet 1.0, developed by Infinite Inc.\n"
              "Written in Python 3.12.6")
        return 0

    def AMIT(self, interpreter: "Interpreter", command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
        """
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        customMsg = None
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpAMIT))
                return 0
        if args:
            customMsg = ' '.join(args.values())

        print("AMIT is GAY!"
              if customMsg is None else
              f"AMIT {customMsg}")
        return 0

    def CD(self, interpreter: "Interpreter", command: str,
           args: dict[int, str], opts: dict[int, str], fullComm: str,
           stream: ty.TextIO, op: str) -> int:
        """
        Changes the current working directory.
        Error code (0-2, 4-6) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpCD))
                return 0

        if len(args) >= 2:
            comm.ERR("Incorrect format")
            return 1

        if args == {}:
            print(os.getcwd())

        elif len(args) == 1:
            # '*' is user directory; '?' goes to prev directory; '/' or
            # '\' is root drive.
            toChangeTo = ''
            path       = args[0].replace('*', os.path.expanduser("~"))
            cwd        = os.getcwd()

            # To navigate back to directory previously in in a certain
            # drive, before changing to another drive. E.g. if the user
            # is in their home directory (C:\Users\<user>) and had changed
            # here to some other drive, say D:, and to come back to same
            # directory in the C: drive, the command would be "cd C:*"
            if len(path) > 1 and path.endswith('?'):
                interpreter.oldPath = cwd
                toChangeTo          = path[:-1]
            elif os.path.isdir(path + os.sep):
                interpreter.oldPath = cwd
                toChangeTo          = path + os.sep
            elif path == '?':
                tempOldPath         = interpreter.oldPath
                interpreter.oldPath = cwd
                toChangeTo          = tempOldPath
            elif path in ('/', '\\'):
                toChangeTo          = '\\'
                interpreter.oldPath = cwd
            else:
                comm.ERR(f"No such directory: '{path}'")
                return 4

            try:
                os.chdir(pl.Path(toChangeTo).resolve())
            except PermissionError:
                comm.ERR(f"Access is denied: \"{path}\"")
                return 5
            except OSError:
                comm.ERR(f"Invalid argument: \"{path}\"")
                return 6

        interpreter.path = os.getcwd()
        return 0

    def CLEAR(self, interpreter: "Interpreter", command: str,
              args: dict[int, str], opts: dict[int, str], fullComm: str,
              stream: ty.TextIO, op: str) -> int:
        """
        Clears the output screen.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                return comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpCLEAR))
                return 0
        if args:
            comm.ERR("Incorrect format")
            return 1
        os.system("cls")
        return interpreter.err

    def COMET(self, interpreter: "Interpreter", command: str,
              args: dict[int, str], opts: dict[int, str], fullComm: str,
              stream: ty.TextIO, op: str) -> int:
        """
        Displays information on the Comet interpreter.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpCOMET))
                return 0
        if args:
            comm.ERR("Incorrect format")
            return 1
        print("The Comet interpreter, version 1.0\nCopyright (c) Infinite "
              "Inc.\nWritten by Thiruvalluvan Kamaraj\nLicenced under the "
              "Apache 2.0 Licence")
        return 0

    def COMMAND(self, interpreter: "Interpreter", command: str,
                args: dict[int, str], opts: dict[int, str], fullComm: str,
                stream: ty.TextIO, op: str) -> int:
        """
        Executes terminal commands.
        Error code (0) (ref. src\\errCodes.txt)
        """
        req = []
        for i in range(len(args) + len(opts)):
            if i in args:
                req.append(args[i])
            elif i in opts:
                req.append('-' + opts[i])
        sp.run(req, shell=True)
        # Revert to original title; may have been changed during execution
        ct.windll.kernel32.SetConsoleTitleW(interpreter.title)
        return 0

    def CREDITS(self, interpreter: "Interpreter", command: str,
                args: dict[int, str], opts: dict[int, str], fullComm: str,
                stream: ty.TextIO, op: str) -> int:
        """
        Displays credits.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpCREDITS))
                return 0
        print("Developed by Infinite Inc.\n"
              "Written by Thiruvalluvan Kamaraj")
        return 0

    def DATE(self, interpreter: "Interpreter", command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
        """
        Displays the current system date.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpDATE))
                return 0
        if args:
            comm.ERR("Incorrect format")
            return 1
        print(dt.datetime.today().strftime("%d-%m-%Y"))
        return 0

    def EXIT(self, interpreter: "Interpreter", command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
        """
        Exits the program.
        Error code (EXIT, 0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpEXIT))
                return 0

        if args:
            comm.ERR("Incorrect format")
            return 1

        # Blarghhh
        raise EOFError

    def GET(self, interpreter: "Interpreter", command: str,
            args: dict[int, str], opts: dict[int, str], fullComm: str,
            stream: ty.TextIO, op: str) -> int:
        """
        Gets an interpreter variable's value.
        Error code (0, 2, 106) (ref. src\\errCodes.txt)
        Error code 106:
            No such variable
        """
        optVals      = comm.lowerLT(opts.values())
        validOpts    = {'h', "-help"}
        toBeSearched = [i for i in args.values()]
        err          = 0

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpGET))
                return 0

        if not toBeSearched:
            for name in interpreter.varTable:
                print(f"'{name}'='{interpreter.varTable[name]}'")
        else:
            for name in toBeSearched:
                if name in comm.lowerLT(interpreter.varTable.keys()):
                    print("'{}'='{}'".format(
                        name,
                        comm.DICTSRCH(name, interpreter.varTable, caseIn=True)[0]
                    ))
                else:
                    # comm.OPTSJOIN() is supposed to be for opts, but... well
                    # I'll just use it for args.
                    comm.ERR(f"No such variable(s): '{name}'")
                    err = err or 106

        return err

    def _builtIn_gen_HELP_HELPER(self, usageInfo: bool) \
            -> tuple[list[str], list[str], int]:
        """
        Helper function of _gen_HELP_HELPER(). Gets the built-in commands and
        their help strings.
        > return: Tuple of commands, their help strings and the maximum
                  length of the command strings
        """
        maxLen          = 0
        commands        = []
        commandHelpStrs = []
        commAppend      = commands.append
        commHelpAppend  = commandHelpStrs.append

        for attr in dir(self):
            if attr.isupper():
                if attr == "ABIRAM" or attr == "AMIT":
                    continue
                maxLen = max(maxLen, len(attr))
                commAppend(attr)
                commHelpAppend(
                    (getattr(self, "help" + attr)[0]
                     if not usageInfo else
                     getattr(self, "help" + attr)[1].removeprefix("USAGE: "))
                )

        return commands, commandHelpStrs, maxLen

    def _ext_gen_HELP_HELPER(self, interpreter: "Interpreter", usageInfo: bool) \
            -> tuple[list[str], list[str], int]:
        """
        Helper function of _gen_HELP_HELPER(). Gets the external commands and
        their help strings.
        > param interpreter: The instance of the Comet interpreter
        > return: Tuple of commands, their help strings and the maximum
                  length of the command strings
        """
        maxLen          = 0
        commands        = []
        commandHelpStrs = []
        commAppend      = commands.append
        commHelpAppend  = commandHelpStrs.append
        binDir          = comm.PTHJN(interpreter.origPth, "bin")

        if not os.path.isdir(binDir):
            return [], [], 0

        for file in os.scandir(binDir):
            # TODO: IMPORTANT: Change the file extensions from .py to .pyd!
            if file.name.startswith('s') and file.name.endswith(".py"):
                # If module was already loaded (should never happen but JIC),
                # delete it from sys.modules
                name = file.name.removeprefix('s').removesuffix(".py").lower()
                try:
                    # Load module and reload to refresh contents
                    mod = il.import_module("bin.s" + name)
                    il.reload(mod)
                    if not hasattr(mod, name.upper()):
                        continue
                    maxLen = max(maxLen, len(name))
                    commAppend(name.upper())
                    if hasattr(mod, "helpStr") and name not in commands:
                        commHelpAppend(
                            (getattr(mod, "helpStr")[0]
                             if not usageInfo else
                             getattr(mod, "helpStr")[1].removeprefix("USAGE: "))
                        )
                    else:
                        commHelpAppend('-')
                    del mod
                    if name in sys.modules:
                        del sys.modules[name]
                except FileNotFoundError:
                    pass

        return commands, commandHelpStrs, maxLen

    def _gen_HELP_HELPER(self, interpreter: "Interpreter",
                         usageInfo: bool) -> int:
        """
        Displays all commands and their help strings.
        > param interpreter: The instance of the Comet interpreter
        > return: Error code (0) (ref. src\\errCodes.txt)
        """
        # Built-in commands
        builtInCommands = self._builtIn_gen_HELP_HELPER(usageInfo)
        commands        = builtInCommands[0]
        commandHelpStrs = builtInCommands[1]
        maxLen          = builtInCommands[2]

        # External commands
        externalCommands = self._ext_gen_HELP_HELPER(interpreter, usageInfo)
        maxLen           = max(maxLen, externalCommands[2])
        commands.extend(externalCommands[0])
        commandHelpStrs.extend(externalCommands[1])

        for i, name in enumerate(commands):
            print(f"{name.lower():<{maxLen}} {commandHelpStrs[i]}")

        return 0

    def _ext_spec_HELP_HELPER(self, interpreter: "Interpreter", arg: str) \
            -> tuple[str, int]:
        """
        Helper function for _spec_HELP_HELPER(). Displays the help message
        for a specific external command.
        > param interpreter: The instance of the Comet interpreter
        > return: Tuple of the help string and the error code (0, 107, 108)
                  (ref. src\\errCodes.txt)
        Error code 107:
            No help string available
        Error code 108:
            No such command
        """
        for item in os.scandir(comm.PTHJN(interpreter.origPth, "bin")):
            if os.path.isdir(item):
                continue
            if not (item.name.startswith('s') and item.name.endswith(".py")):
                continue
            if not item.name == 's' + arg.lower() + ".py":
                continue

            # If module has been already loaded (should never happen),
            # delete it from sys.modules
            name = item.name.removeprefix('s').removesuffix(".py").lower()
            try:
                # Load module and reload to refresh its contents
                mod = il.import_module("bin.s" + name)
                il.reload(mod)
                # Module MUST have a function with the command name
                # in uppercase to be recognised as a command
                if not hasattr(mod, name.upper()):
                    continue
                if hasattr(mod, "helpStr"):
                    tmp = getattr(mod, "helpStr")
                    break
                else:
                    comm.ERR(f"No help string available: \"{arg}\"")
                    return '', 107
            except FileNotFoundError:
                pass

        else:
            comm.ERR(f"No such command: \"{arg}\"", sl=5)
            return '', 108

        return tmp, 0

    def _spec_HELP_HELPER(self, interpreter: "Interpreter", arg: str) -> int:
        """
        Displays the help message for a specific command.
        > param interpreter: The instance of the Comet interpreter
        > param args: Dictionary of arguments
        > return: Error code (0, 107, 108) (ref. src\\errCodes.txt)
        Error code 107:
            No help string available
        Error code 108:
            No such command
        """
        if arg.lower() == "please":
            print(";)")
            return 0

        try:
            if "help" + arg.upper() in self.__dict__:
                print('\n'.join(
                    line.expandtabs(4)
                    for line in self.__dict__["help" + arg.upper()]
                ))
                return 0

            tmp = self._ext_spec_HELP_HELPER(interpreter, arg)
            if tmp[1] != 0:
                return tmp[1]
            print(f"COMMAND: {arg.lower()}")
            print('\n'.join(line.expandtabs(4) for line in tmp[0]))
            return 0

        except AttributeError:
            comm.ERR(f"No help string: \"{arg}\"", sl=4)
            return 107

        except KeyError:
            comm.ERR(f"No such command: \"{arg}\"", sl=4)
            return 108

    def HELP(self, interpreter: "Interpreter", command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
        """
        Displays the main help messages, and command-specific help messages.
        Error code (0-2, 107, 108) (ref. src\\errCodes.txt)
        Error code 107:
            No help string available
        Error code 108:
            No such command
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'s', 'u', 'h',
                     "-syntax", "-usage", "-help"}
        usageInfo = False
        err       = 0

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpHELP))
                return 0
            for opt in optVals:
                if opt == 's' or opt == "-syntax" or opt == 'u' or opt == "-usage":
                    if args:
                        comm.ERR(f"Cannot use -{opt} when supplying arguments")
                        return 3
                    usageInfo = True

        if not args:
            err = self._gen_HELP_HELPER(interpreter, usageInfo)
        else:
            for arg in args.values():
                tmp = self._spec_HELP_HELPER(interpreter, arg)
                err = err or tmp

        return err

    def INTRO(self, interpreter: "Interpreter", command: str,
              args: dict[int, str], opts: dict[int, str], fullComm: str,
              stream: ty.TextIO, op: str) -> int:
        """
        Displays the intro message.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpINTRO))
                return 0
        if args:
            comm.ERR("Incorrect format")
            return 1
        print(interpreter.introTxt)
        return 0

    def QUIT(self, interpreter: "Interpreter", command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
        """
        Quits the program.
        Error code (EXIT, 0, 1, 2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpQUIT))
                return 0

        if args:
            comm.ERR("Incorrect format")
            return 1

        raise EOFError

    def RUNPATH(self, interpreter: "Interpreter", command: str,
                args: dict[int, str], opts: dict[int, str], fullComm: str,
                stream: ty.TextIO, op: str) -> int:
        """
        Displays the path Comet is running from.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpRUNPATH))
                return 0

        if args:
            comm.ERR("Incorrect format")
            return 1

        print(interpreter.origPth)
        return 0

    def set_SET_HELPER(self, interpreter: "Interpreter",
                      args: dict[int, str]) -> int:
        """
        Helper function for the set feature of the set command.
        > param interpreter: The instance of the Comet interpreter
        > param args: Dictionary of arguments
        > return: Error code (0, 1, 105) (ref. src\\errCodes.txt)
        Error code 105:
            Attempted modification of protected variable
        """
        if len(args) != 2:
            comm.ERR("Incorrect format", sl=4)
            return 1

        if comm.lowerLT(args)[0] == "error":
            comm.ERR("Operation not allowed; cannot edit "
                     "var 'error'", sl=4)
            return 105

        sortedArgs = sorted(args)
        varName    = args[sortedArgs[0]]
        varVal     = args[sortedArgs[1]]
        if keys := comm.DICTSRCH(varName, interpreter.varTable, caseIn=True,
                                 returnMode="keys"):
            for key in keys:
                interpreter.varTable.pop(key)
        interpreter.varTable[varName] = varVal
        return 0

    def rm_SET_HELPER(self, interpreter: "Interpreter",
                      args: dict[int, str]) -> int:
        """
        Helper function for the remove feature of the set command.
        > param interpreter: The instance of the Comet interpreter
        > param args: Dictionary of arguments
        > return: Error code (0, 1, 105, 106) (ref. src\\errCodes.txt)
        Error code 105:
            Attempted modification of protected variable
        Error code 106:
            No such variable
        """
        err = 0

        if not args:
            comm.ERR("Incorrect format", sl=4)
            return 1

        for arg in args.values():
            if arg.lower() == "error":
                comm.ERR("Operation not allowed; cannot "
                         "remove var 'error'", sl=4)
                err = err or 105
                continue

            if not (keys := comm.DICTSRCH(arg, interpreter.varTable,
                                          caseIn=True, returnMode="keys")):
                comm.ERR(f"No such variable: '{arg}'", sl=4)
                err = err or 106
                continue

            for key in keys:
                interpreter.varTable.pop(key)

        return err

    def SET(self, interpreter: "Interpreter", command: str,
            args: dict[int, str], opts: dict[int, str], fullComm: str,
            stream: ty.TextIO, op: str) -> int:
        """
        Sets interpreter variables.
        Error code (0-2, 105, 106) (ref. src\\errCodes.txt)
        Error code 105:
            Attempted modification of protected variable
        Error code 106:
            No such variable
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'r', 'h', "-remove", "-help"}
        remove    = False

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpSET))
                return 0
            for opt in optVals:
                if opt == 'r' or opt == '-remove':
                    remove = True

        if not args:
            comm.ERR("Incorrect format")
            return 1

        if not remove:
            return self.set_SET_HELPER(interpreter, args)
        else:
            return self.rm_SET_HELPER(interpreter, args)

    def STOP(self, interpreter: "Interpreter", command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
        """
        Pauses the interpreter and waits for user to press any key.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpSTOP))
                return 0

        if args:
            comm.ERR("Incorrect format")
            return 1

        stream.write("Input a key to continue: ")
        stream.flush()
        key = ms.getch()
        while ms.kbhit():
            ms.getch()
        stream.write(str(ord(key)) + '\n')
        stream.flush()
        return 0

    def TIME(self, interpreter: "Interpreter", command: str,
             args: dict[int, str], opts: dict[int, str], fullComm: str,
             stream: ty.TextIO, op: str) -> int:
        """
        Displays the current system time.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpTIME))
                return 0

        if args:
            comm.ERR("Incorrect format")
            return 1

        print(dt.datetime.now().strftime('%H:%M.%S.%f'))
        return 0

    def TIMEIT(self, interpreter: "Interpreter", command: str,
               args: dict[int, str], opts: dict[int, str], fullComm: str,
               stream: ty.TextIO, op: str) -> int:
        """
        Time the execution of a command.
        Error code (0) (ref. src\\errCodes.txt)
        """
        startTime = ti.default_timer()
        interpreter.execute(fullComm.strip().removeprefix(command).strip())
        print(f"elapsed {round(ti.default_timer() - startTime, 6)}s")
        return 0

    def TITLE(self, interpreter: "Interpreter", command: str,
              args: dict[int, str], opts: dict[int, str], fullComm: str,
              stream: ty.TextIO, op: str) -> int:
        """
        Sets the title of the console window.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpTITLE))
                return 0

        if not args:
            interpreter.title = self.mainFlTitle
        elif len(args) != 1:
            comm.ERR("Incorrect format")
            return 1
        for arg in args.values():
            interpreter.title = arg

        ct.windll.kernel32.SetConsoleTitleW(interpreter.title)
        return 0

    def VER(self, interpreter: "Interpreter", command: str,
            args: dict[int, str], opts: dict[int, str], fullComm: str,
            stream: ty.TextIO, op: str) -> int:
        """
        Displays the version of the Comet interpreter.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpVER))
                return 0
        if args:
            comm.ERR("Incorrect format")
            return 1
        print(interpreter.version)
        return 0

    def WHEREIS(self, interpreter: "Interpreter", command: str,
                args: dict[int, str], opts: dict[int, str], fullComm: str,
                stream: ty.TextIO, op: str) -> int:
        """
        Displays the location of a command.
        > param interpreter: Interpreter object
        > param command: Command name
        > param args: Dictionary of arguments
        > param opts: Dictionary of options
        > param fullComm: Full input line
        > param stream: Original STDOUT
        > return: Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'h', "-help"}
        err       = 0

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpWHEREIS))
                return 0

        if not args:
            comm.ERR("Incorrect format")
            return 1

        builtInComms = [i for i in dir(interpreter.builtInComms) if i.isupper()]
        binDir       = comm.PTHJN(interpreter.origPth, "bin")
        dirCntnts    = []
        if os.path.isdir(binDir):
            dirCntnts = [i for i in os.scandir(binDir)]

        for arg in args.values():
            if arg.upper() in builtInComms:
                print(f"{arg}: Built-in")
                continue

            for fl in dirCntnts:
                if not (os.path.isfile(fl) and fl.name.endswith(".py") \
                        and fl.name.startswith('s')):
                    continue
                if fl.name.lower() != 's' + arg.lower() + ".py":
                    continue

                # TODO: IMPORTANT: Change the extension to .pyd!
                modulePath = comm.PTHJN(interpreter.origPth, "bin",
                                        's' + arg + ".py")
                spec       = ilu.spec_from_file_location(arg, modulePath)
                module     = None

                if spec is None or spec.loader is None:
                    continue

                try:
                    module = ilu.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, arg.upper()):
                        print(f"{arg}: {fl.path}")
                        break
                except (AttributeError, ImportError, FileNotFoundError, OSError):
                    pass

            else:
                comm.ERR(f"No such (valid) command: \"{arg}\"")
                err = err or 113

        return err


class Interpreter:
    def __init__(self, parser: Parser, settings: dict[str, str],
                 title: str) -> None:
        self.varTable: dict[str, str]
        self.introTxt     = ("Comet 1.0\nLicence: Apache-2.0")
        self.version      = "1.0"
        self.err          = 0
        self.parser       = parser
        self.settings     = settings
        self.origPth      = comm.ORIGPTH
        self.path         = self.settings.get("path")
        self.title        = self.settings.get("title")
        self.intro        = self.settings.get("intro")
        self.varTable     = {"bookmark": os.path.expanduser('~'),
                             "bm": os.path.expanduser('~'),
                             "error": '0'}
        self.builtInComms = BuiltInComms(title)

        if self.path is not None and self.path != '':
            self.path = str(pl.Path(self.path).resolve())
        elif self.path is None or self.path == '':
            self.path = comm.DEFLTSETT["path"]
        if self.title is None or self.title == '':
            self.title = title
        if self.intro is None or self.intro == '':
            self.intro = "off"
        if self.intro == "on":
            print(self.introTxt)
        elif self.intro != "off":
            comm.WARN("Invalid value for attribute 'intro' in settings file",
                      raiser="comet")

        self.doesPathsExist()
        self.oldPath = self.path
        os.chdir(self.path)
        ct.windll.kernel32.SetConsoleTitleW(self.title)

        self.aliases = {}
        try:
            with open(comm.PTHJN(self.origPth, "_aliases.txt"),
                    buffering=1) as f:
                for line in f:
                    alias, sym, value = line.partition('=')
                    if sym == '':
                        continue
                    self.aliases[alias] = value.removesuffix('\n')
        except FileNotFoundError:
            try:
                open(comm.PTHJN(self.origPth, "_aliases.txt"), 'w').close()
            except PermissionError:
                comm.ERR("Access is denied; unable to create alias file")

        # Plugin executions
        try:
            for item in os.scandir(comm.PTHJN(self.origPth, "plugins")):
                if not os.path.isfile(item):
                    continue
                with open(item) as f:
                    for line in f:
                        self.execute(line.strip('\n'))
        except FileNotFoundError:
            pass
        except PermissionError:
            comm.ERR("Access is denied: "
                     f"\"{comm.PTHJN(self.origPth, "plugins")}\";"
                     "Cannot execute plugin file(s)")

    def doesPathsExist(self) -> None:
        "Check if the startup path (in the config file) exists."
        if not os.path.isdir(self.path):
            comm.WARN("Startup path does not exist. Using default path",
                      raiser="comet")
            self.path = comm.DEFLTSETT["path"]

    def parse(self, line: str) -> \
            list[tuple[str, dict[int, str], dict[int, str]] | str]:
        self.parser.src = line
        return self.parser.parse(self.varTable)

    def getFunc(self, command: str) -> tuple[
            ty.Callable[["Interpreter", str, dict[int, str], dict[int, str],
                         str, bool], int], int] | str | float | int | None:
        """
        Get the function to be called from the modules in directory "src\\bin".
        > param command: Command name. Used to fetch the function from the
                         appropriate module
        > return: A function, an integer (-1) for unknown errors (and fatal
                  errors) or None if the function is not found.
        ----------
        Dev note:
        Yeah, I know this is perhaps horrible and dirty code, but I wanted it
        this way so that the command file is imported every time, thus making
        live updates possible.
        """
        # Commands dependent on dir "bin" will fail if the dir is removed or
        # made inaccessible due to some race condition. Don't really want to
        # check for the existance of "bin" in every command as it would be
        # really messy
        # if not os.path.isdir(self.origPth + os.sep + "bin"):
        #     return 4

        if hasattr(self.builtInComms, command.upper()):
            func = getattr(self.builtInComms, command.upper())
            return func

        # Reckon case-insensitive search is required as Windows has a
        # case-insensitive file system
        searchResult = comm.DICTSRCH('s' + command, sys.modules, caseIn=True)
        if searchResult is None:
            return -1
        elif len(searchResult) > 1:
            return comm.ERR("Multiple commands with same name detected; "
                            "possible name conflict between an interpreter "
                            "module and a command file", raiser="comet")
        elif len(searchResult) == 1:
            try:
                sys.modules.pop(searchResult[0])
            except KeyError:
                pass

        if command.startswith('?'):
            return self.getFunc("help")
        elif command.startswith('!'):
            return self.getFunc("command")
        elif command.startswith('#'):
            return self.err

        try:
            # TODO: IMPORTANT: Change the extension to .pyd!
            modulePath = comm.PTHJN(self.origPth, "bin", 's' + command + ".py")
            spec       = ilu.spec_from_file_location(command, modulePath)
        except ValueError:
            # Raised if path is too long
            return 3

        if spec is None:
            return comm.UNERR("Could not get run function",
                              "Could not get run function; Might be due to "
                              "a permission issue or invalid command name")
        elif spec.loader is None:
            return comm.UNERR("Could not get run function",
                              "Could not get run function; Unknown cause")

        func   = None
        module = None

        try:
            module = ilu.module_from_spec(spec)
            spec.loader.exec_module(module)
            func   = getattr(module, command.upper())

        except (AttributeError, ImportError, FileNotFoundError):
            import traceback
            traceback.print_exc()
            func = self.aliases[command] if command in self.aliases else None

        except OSError:
            pass

        finally:
            sys.modules = comm.caseINSensModSearchAndRm(command, sys.modules)
            del module

        return func

    def _before(self) -> None:
        "Called before every execution of execute()"
        pass

    def _after(self) -> None:
        "Called after every execution of execute()"
        pass

    def execute(self, line: str, before: bool=True, after: bool=True) -> int:
        """
        Parse the input line, get the run function for the command, and call
        it (obviously).
        > param line: Line to execute
        > param before: Boolean to inform if function self._before() needs to
                        be executed at the start every time this function is
                        called
        > param after: Boolean to inform if function self._after() needs to
                       be executed at the end every time this function is
                       called
        """
        self._before() if before else None
        all      = self.parse(line)
        pipeOut  = None
        redirOut = None

        while all:
            args: dict[int, str]
            opts: dict[int, str]
            command, args, opts = all.pop(0)
            operation           = ''

            if all:
                operation = all.pop(0)

            if len(command) == 1 and ord(command) in (26, 4):
                # Ughhh. Will be caught in the main module
                raise EOFError

            if command == "$?" and not args and not opts:
                print(self.err)
                return self.err

            if [i for i in args if len(args[i]) == 1 and ord(args[i]) == 26]:
                return self.err

            if [i for i in opts if len(opts[i]) == 1 and ord(opts[i]) == 26]:
                return self.err

            if command.startswith(('!', '?')):
                tempArgs: dict[int, str]
                tempOpts: dict[int, str]
                tempArgs = {}
                tempOpts = {}
                if command[1:]:
                    for arg in args:
                        tempArgs[arg + 1] = args[arg]
                    for opt in opts:
                        tempOpts[opt + 1] = opts[opt]
                    tempArgs[0] = command[1:]
                command = command[0]
                args.update(tempArgs)
                opts.update(tempOpts)

            if not command:
                return self.err

            func      = self.getFunc(command)
            capture   = io.StringIO()
            oldStdOut = sys.__stdout__

            if isinstance(func, ty.Callable):
                if pipeOut is not None:
                    try:
                        maxPos = max(list(args) + list(opts)) + 1
                    except ValueError:
                        maxPos = 0
                    args[maxPos] = pipeOut

                with cl.redirect_stdout(capture):
                    self.err = func(self, command, args, opts, line, oldStdOut,
                                    "pipe" if pipeOut is not None else '')

                pipeOut = None
                output  = capture.getvalue()
                if operation is None or operation in "&^;":
                    print(output, end='')
                    if operation == '&' and self.err:
                        break
                elif operation == '|':
                    pipeOut = output
                elif operation == '>':
                    redirOut = output

            elif isinstance(func, str):
                tempOptDict: dict[int, str] = {}
                for key in opts:
                    tempOptDict[key] = '-' + opts[key]
                err = self.execute(
                    func + ' ' + ' '.join(
                        comm.DICTUPDATE(args, tempOptDict).values()
                    ),
                    before=False
                )
                return err

            elif os.path.isfile(command):
                try:
                    with open(command) as f:
                        for line in f:
                            self.err = self.execute(line.removesuffix('\n'),
                                                    before=before, after=after)
                except UnicodeDecodeError:
                    comm.ERR("Does not appear to contain valid UTF-8: "
                             f"\"{pl.Path(command).resolve()}\"",
                             raiser="comet")
                    self.err = 9
                except PermissionError:
                    comm.ERR("Access is denied: "
                             f"\"{pl.Path(command).resolve()}\"",
                             raiser="comet")
                    self.err = 5

            elif command == '.' or command == ".." or \
                    (command.endswith('\\' or '/') and os.path.isdir(command)):
                if args or opts:
                    self.err = comm.ERR("Run cd command to use arguments and "
                                        "options", raiser="comet")
                self.builtInComms.CD(self, "cd", {0: command}, {}, line,
                                     oldStdOut, operation)

            else:
                if func == 2:
                    return self.err
                self.err = 2 if func is None else -1
                if func == 3:
                    comm.ERR("Command too long", raiser="comet")
                elif func == 4:
                    comm.ERR("Directory \"bin\" was not found", raiser="comet")
                elif func is None:
                    comm.ERR(f"Bad command: \"{command}\"", raiser="comet")

        self._after() if after else None
        self.varTable["error"] = str(self.err)
        return 0
