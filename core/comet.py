#
# Comet 1 source code
# Infinite Inc.
# Copyright (c) 2025 Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename: src\\core\\comet.py
# Description: Contains the Comet interpreter, the parser, and the built-in
#              commands
#

import io
import os
import sys
import time
import contextlib     as cl
import ctypes         as ct
import datetime       as dt
import importlib      as il
import importlib.util as ilu
import msvcrt         as ms
import pathlib        as pl
import subprocess     as sp
import threading      as th
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
    > - STDOUT REDIRECTION
    @ - STDERR REDIRECTION
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
            # '@': 105,
            # '<': -1
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
        """
        TODO: Edit the parameters part! Remove unnecessary development comments!
        Read an unquoted argument.
        > param varTable: The variable table (will be used later for variable substitution)
        > return: The parsed unquoted argument
        """
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
                self.pos -= 1

            self._rdChar()

        return self.src[startPos:self.pos]

    def _rdQuotedCommOrArg(self, quote: str, varTable: dict[str, str]) -> str | int:
        """
        TODO: Edit the parameters part! Remove unnecessary development comments!
        Read a quoted command/argument.
        > param quote: The quote character
        > param varTable: The variable table (will be used later for variable substitution)
        > return: The parsed quoted argument or integer error code
            1: Unexpected end of line while parsing the quoted argument, i.e.
               missing closing quote
        """
        startPos = self.pos
        self._rdChar()
        while self.char != quote:
            # Missing closing quote
            if self.char == '\0':
                return 1

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
                self.pos -= 1

            self._rdChar()

        return self.src[startPos+1:self.pos]

    def _rdOpt(self) -> str:
        """
        TODO: Edit the parameters part! Remove unnecessary development comments!
        Read an option.
        > return: The parsed option
        """
        stPos = self.pos
        self._rdChar()
        while not self.char.isspace() and self.char not in self.spChars:
            if self.char == '\0':
                return self.src[stPos+1:self.pos+1]
            self._rdChar()
        return self.src[stPos+1:self.pos]

    def _rdComm(self, varTable: dict[str, str]) -> str | int:
        """
        TODO: Edit the parameters part! Remove unnecessary development comments!
        Read the command name in the input line.
        > param varTable: The variable table (used for other functions; TODO: Remove!)
        > return: The parsed quoted argument or integer error code
            1: Unexpected end of line while parsing the quoted command, i.e.
               missing closing quote
        """
        startPos = self.pos
        # Quoted command/file
        if (quote := self.char == '"') or self.char == '\'':
            tmp = self._rdQuotedCommOrArg('"' if quote else '\'', varTable)
            self._rdChar()
            return tmp
        self._rdChar()
        while not self.char.isspace() and self.char not in self.spChars:
            if self.char == '\0':
                return self.src[startPos:self.pos+1]
            self._rdChar()
        return self.src[startPos:self.pos]

    def parse(self, varTable: dict[str, str]) \
            -> list[tuple[str, dict[int, str], dict[int, str]] | str] | int:
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

        command = self._rdComm(varTable)
        if isinstance(command, int):
            if command == 1:
                comm.ERR("Unclosed quoted command", raiser="comet")
            return command

        while self.char != '\0':
            if self.char.isspace():
                self._rdChar()
                continue

            if self.char in self.spChars:
                curSpChar       = self.char
                self.src        = self.src[self.pos+1:]
                subCommandParse = self.parse(varTable)
                if isinstance(subCommandParse, int):
                    return subCommandParse
                full += [(command, args, opts), curSpChar, *subCommandParse]
                return full

            if (temp := (self.char == '\'')) or self.char ==  '"':
                arg = self._rdQuotedCommOrArg('\'' if temp else '"', varTable)
                if isinstance(arg, int):
                    if arg == 1:
                        comm.ERR("Unclosed quoted argument", raiser="comet")
                    return arg
                args[count] = arg

            elif self.char == '-' and not self._pkChar().isspace() \
                    and self._pkChar() != '\0':
                opt         = self._rdOpt()
                opts[count] = opt

            elif self.char != ' ':
                arg         = self._rdUnquotedArg(varTable)
                args[count] = arg

            # Needs to be repeated even though the exact same block is present
            # above, to account for cases such as when the special character is
            # present just after an option without any whitespae, etc.
            if self.char in self.spChars:
                curSpChar          = self.char
                self.src           = self.src[self.pos+1:]
                otherCommandsParse = self.parse(varTable)
                if isinstance(otherCommandsParse, int):
                    return otherCommandsParse
                full += [(command, args, opts), curSpChar, *otherCommandsParse]
                return full

            count += 1
            self._rdChar()

        full.append((command, args, opts))
        return full


class BuiltInComms:
    """
    The command functions have the following parameters:
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Arguments of the command
    > param opts: Options of the command
    > param fullComm: Full prompt line
    > param stream: Original stdout
    > param op: Operation next in line to be performed
    > return: Error code (ref. src\\errCodes.txt)
    """
    def __init__(self, interpreter: "Interpreter", mainFlTitle: str) -> None:
        self.interpreter   = interpreter
        self.mainFlTitle   = mainFlTitle

        # I'm sorry.
        self.helpABIRAM    = ("Prints out a fact.", '', "USAGE: abiram [-h]",
                              '', "OPTION(S)", "-h / --help", "\tHelp message")
        self.helpABOUT     = ("Displays information about Comet.", '',
                              "USAGE: about [-h]", '', "OPTION(S)",
                              "-h / --help", "\tHelp message")
        self.helpAMIT      = (
            "Mocks Amit.", '', "USAGE: amit [-h] [msg ...]", '', "ARGUMENT(S)",
            "None", "\tPrints the default output", "msg",
            "\tCustom message", '', "OPTION(S)", "-h / --help",
            "\tHelp message"
        )
        self.helpCD        = (
            "Changes the current working directory.", "USAGE: cd [-h] [path]",
            '', "ARGUMENT(S):", "None", "\tPrints current working directory",
            "path", "\tDirectory to change to", "\t* - User directory",
            "\t? - Previous working directory",
            "\tDRV:? - Change to previous working directory on drive DRV",
            "\t\\ or / - Root directory for current drive", '',
            "OPTION(S)", "-h / --help", "\tHelp message"
        )
        self.helpCLEAR     = ("Clears the output screen.", '',
                              "USAGE: clear [-h]", '', "OPTION(S)",
                              "-h / --help", "\tHelp message")
        self.helpCOMET     = (
            "Displays information on the Comet interpreter.", '',
            "USAGE: comet [-h]", '', "OPTION(S):", "-h / --help",
            "\tHelp message", '',
            "If your terminal lets the application to handle these keys, "
                "you can use them for the following.",
            "SPECIAL KEYS",
            "^a - Move the cursor to the beginning of the line",
            "^b - Move the cursor back one character"
            "^c - Interrupt the interpreter",
            "^d - Exit the interpreter",
            "^e - Move the cursor to the end of the line",
            "^f - Move the cursor forward one character",
            "^k - Erase current input line from cursor till EOL",
            "^l - \"Clear\" the screen (scrolls the buffer)",
            "^n / down arrow - Scroll down the history",
            "^p / up arrow - Scroll up the history",
            "^r - Reverse i-search history",
            "^s - Forward i-search",
            "^t - Transpose characters",
            "^u - Erase current input line from cursor till beginning of line",
            "^w - Erase current input line from cursor till last word boundary",
            "^y - Recall deleted line",
            "^z + return - Exit the interpreter", '',
            "ESCAPE CHARACTERS RECOGNISED BY THE INTERPRETER",
            "\\\\ - Backslash (\\)",
            "\\n - Newline",
            "\\' - Single quote (')",
            "\\\" - Double quote (\")",
        )
        self.helpCOMMAND   = (
            "Run terminal commands.", '', "USAGE: command ln", '',
            "ARGUMENT(S)", "ln", "\tLine to be executed in terminal",
            '', "\tHelp message", '', "NOTE",
            "-h and --help options are unavailable for this command due to "
            "complications with parsing.", "Use 'help command' for its help text."
        )
        self.helpDATE      = ("Displays the current system date.", '',
                              "USAGE: date [-h]", '',
                              "OPTION(S)", "-h / --help", "\tHelp message")
        self.helpCREDITS   = ("Displays credits.", '', "USAGE: credits [-h]",
                              '', "OPTION(S)", "-h / --help", "\tHelp message")
        self.helpEXIT      = ("Exits the program.", '', "USAGE: exit [-h]", '',
                              "OPTION(S)", "-h / --help", "\tHelp message")
        self.helpGET       = (
            "Gets an interpreter variable's value.", '',
            "USAGE: get [-h] [var]", '', "ARGUMENT(S)", "var",
            "\tVariable to be accessed", '', "OPTION(S)", "-h / --help",
            "\tHelp message"
        )
        self.helpHELP      = (
            "Displays the help menu.", '', "USAGE: help [-h] [command ...]",
            '', "ARGUMENT(S)", "command", "\tCommand to display help text for",
            '', "OPTION(S)", "-h / --help", "\tHelp message"
        )
        self.helpINTRO     = ("Displays the startup string.", '',
                              "USAGE: intro [-h]", '', "OPTION(S)",
                              "-h / --help", "\tHelp message")
        self.helpPWD       = ("Displays the current working directory.", '',
                              "USAGE: pwd [-h]", '', "OPTION(S)",
                              "-h / --help", "\tHelp message")
        self.helpQUIT      = ("Exits the program.", '', "USAGE: quit [-h]", '',
                              "OPTION(S)", "-h / --help", "\tHelp message")
        self.helpRUNPATH   = ("Print the path from where the interpreter is "
                              "running.", '', "USAGE: runpath [-h]", '',
                              "OPTION(S)", "-h / --help", "\tHelp message")
        self.helpSET       = (
            "Sets interpreter variables.", '',
            "USAGE: set [-h] (name value | -r name ...)", '', "ARGUMENT(S)",
            "name", "\tName of the variable", "value",
            "\tValue of the variable", '', "OPTION(S)", "-h / --help",
            "\tHelp message", "-s / --set", "\tSet an interpreter variable",
            "-r / --remove", "\tRemove an interpreter variable"
        )
        self.helpSTOP      = (
            "Pauses the program and waits for user to press any key.", '',
            "USAGE: stop [-h]", '', "OPTION(S)", "-h / --help",
            "\tHelp message"
        )
        self.helpTIME      = ("Displays the current system time.", '',
                              "USAGE: time [-h]", '', "OPTION(S)",
                              "-h / --help", "\tHelp message")
        self.helpTIMEIT    = (
            "Time the execution of a command.", '', "USAGE: timeit ln", '',
            "ARGUMENT(S)", "ln", "\tLine to be executed", '', "NOTE",
            "-h and --help options are unavailable for this command due to "
                "complications with parsing.",
            "Use 'help timeit' for its help text."
        )
        self.helpTITLE     = (
            "Changes the title of the console window.", '',
            "USAGE: title [-h] [str]", '', "ARGUMENT(S)", "None",
            "\tRevert to original title", "str",
            "\tNew title of the console window", '', "OPTION(S)",
            "-h / --help", "\tHelp message"
        )
        self.helpVER       = ("Displays the version of Comet interpreter.", '',
                              "USAGE: ver [-h]", '', "OPTION(S)", "-h / --help",
                              "\tHelp message")
        self.helpWHEREIS   = (
            "Display the locations of commands.", '',
            "USAGE: whereis [-h] command ...", '', "ARGUMENT(S)", "command",
            "\tName of the command", '', "OPTION(S)", "-h / --help",
            "\tDisplay help message"
        )

    def ABIRAM(self, varTable: dict[str, str], origPth: str, prevErr: int,
               command: str, args: dict[int, str], opts: dict[int, str],
               fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Prints out a fact.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def ABOUT(self, varTable: dict[str, str], origPth: str, prevErr: int,
              command: str, args: dict[int, str], opts: dict[int, str],
              fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays the "about" of Comet.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def AMIT(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Mocks Amit.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def CD(self, varTable: dict[str, str], origPth: str, prevErr: int,
           command: str, args: dict[int, str], opts: dict[int, str],
           fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Changes the current working directory.
        Error code (0-2, 4-6) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpCD))
                return 0

        if len(args) >= 2 or args == {}:
            comm.ERR("Incorrect format")
            return 1

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
                self.interpreter.oldPath = cwd
                toChangeTo          = path[:-1]
            elif os.path.isdir(path + os.sep):
                self.interpreter.oldPath = cwd
                toChangeTo          = path + os.sep
            elif path == '?':
                tempOldPath         = self.interpreter.oldPath
                self.interpreter.oldPath = cwd
                toChangeTo          = tempOldPath
            elif path in ('/', '\\'):
                toChangeTo          = '\\'
                self.interpreter.oldPath = cwd
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

        self.interpreter.path = os.getcwd()
        return 0

    def CLEAR(self, varTable: dict[str, str], origPth: str, prevErr: int, command: str,
              args: dict[int, str], opts: dict[int, str], fullComm: str,
              stream: ty.TextIO, op: str) -> int:
        """
        Clears the output screen.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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
        return prevErr

    def COMET(self, varTable: dict[str, str], origPth: str, prevErr: int,
              command: str, args: dict[int, str], opts: dict[int, str],
              fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays information on the Comet interpreter.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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
              "Apache 2.0 Licence\nSpecial thanks to prompt_toolkit "
              "(https://github.com/prompt-toolkit/python-prompt-toolkit)")
        return 0

    def COMMAND(self, varTable: dict[str, str], origPth: str, prevErr: int,
                command: str, args: dict[int, str], opts: dict[int, str],
                fullComm: str, stream: ty.TextIO, op: str) -> int:
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
        ct.windll.kernel32.SetConsoleTitleW(self.interpreter.title)
        return 0

    def CREDITS(self, varTable: dict[str, str], origPth: str, prevErr: int,
                command: str, args: dict[int, str], opts: dict[int, str],
                fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays credits.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def DATE(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays the current system date.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def EXIT(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Exits the program.
        Error code (EXIT, 0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def GET(self, varTable: dict[str, str], origPth: str, prevErr: int,
            command: str, args: dict[int, str], opts: dict[int, str],
            fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Gets an interpreter variable's value.
        Error code (0, 2, 106) (ref. src\\errCodes.txt)
        Error code 106:
            No such variable
        """
        optVals      = comm.LOWERLT(opts.values())
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
            for name in varTable:
                print(f"'{name}'='{varTable[name]}'")
        else:
            for name in toBeSearched:
                tmp = comm.DICTSRCH(name, varTable, caseIn=True)
                if tmp is not None:
                    print(f"{name}='{tmp[0]}'")
                else:
                    comm.ERR(f"No such variable: '{name}'")
                    err = err or 106

        return err

    def _builtIn_gen_HELP_HELPER(self, usageInfo: bool) \
            -> tuple[list[str], list[str], int]:
        """
        Helper function of _gen_HELP_HELPER(). Gets the built-in commands and
        their help strings.
        > param usageInfo: True if the user had asked for usage to be displayed
        > return: Tuple of commands, their help strings and the maximum
                  length of the command strings
        """
        maxLen          = 0
        commands        = []
        commandHelpStrs = []
        commAppend      = commands.append
        commHelpAppend  = commandHelpStrs.append

        for attr in dir(self):
            if not attr.isupper() or attr == "ABIRAM" or attr == "AMIT":
                continue
            maxLen = max(maxLen, len(attr))
            commAppend(attr)
            if not hasattr(self, "help" + attr):
                commHelpAppend('-')
                continue
            try:
                strippedHelpStr = getattr(self, "help" + attr)
                commHelpAppend(
                    strippedHelpStr[0] if not usageInfo else
                    strippedHelpStr[1].removeprefix("USAGE: ")
                )
            except IndexError:
                comm.ERR(f"Invalid help string: '{attr.lower()}'", sl=5)
                commHelpAppend("[INVALID]")

        return commands, commandHelpStrs, maxLen

    def _ext_gen_HELP_HELPER(self, origPth: str, usageInfo: bool) \
            -> tuple[list[str], list[str], int]:
        """
        Helper function of _gen_HELP_HELPER(). Gets the external commands and
        their help strings.
        > param origPth: Path of the interpreter
        > return: Tuple of commands, their help strings and the maximum
                  length of the command strings
        """
        maxLen          = 0
        commands        = []
        commandHelpStrs = []
        commAppend      = commands.append
        commHelpAppend  = commandHelpStrs.append
        binDir          = comm.PTHJN(origPth, "bin")

        if not os.path.isdir(binDir):
            return [], [], 0

        for fl in os.scandir(binDir):
            # TODO: IMPORTANT: Change the file extensions from .py to .pyd!
            if fl.name.startswith('s') and fl.name.endswith(".py"):
                name = fl.name.removeprefix('s').removesuffix(".py").lower()

                try:
                    # Load module and reload to refresh contents
                    mod = il.import_module("bin.s" + name)
                    il.reload(mod)
                    if not hasattr(mod, name.upper()):
                        continue
                    maxLen = max(maxLen, len(name))
                    commAppend(name.upper())

                    if hasattr(mod, "helpStr") and name not in commands:
                        try:
                            strippedHelpStr = [
                                i for i in getattr(mod, "helpStr") if i
                            ]
                            commHelpAppend(
                                (strippedHelpStr[0]
                                if not usageInfo else
                                strippedHelpStr[1].removeprefix("USAGE: "))
                            )
                        except IndexError:
                            comm.ERR(f"Invalid help string: '{name.lower()}'",
                                     sl=5)
                            commHelpAppend("[INVALID]")
                            continue
                    else:
                        commHelpAppend('-')

                    del mod
                    if name in sys.modules:
                        del sys.modules[name]

                except FileNotFoundError:
                    pass

        return commands, commandHelpStrs, maxLen

    def _gen_HELP_HELPER(self, origPth: str, usageInfo: bool) -> int:
        """
        Displays all commands and their help strings.
        > param origPth: Path of the interpreter
        > return: Error code (0) (ref. src\\errCodes.txt)
        """
        bltInComms = self._builtIn_gen_HELP_HELPER(usageInfo)
        extComms   = self._ext_gen_HELP_HELPER(origPth, usageInfo)
        maxLen     = max(bltInComms[2], extComms[2])

        commands    = bltInComms[0] + extComms[0]
        commHlpStrs = bltInComms[1] + extComms[1]

        for i, name in enumerate(commands):
            print(f"{name.lower():<{maxLen}} {commHlpStrs[i]}")
            # print(
            #     (f"{name.lower():<{maxLen}} " if not usageInfo else '')
            #     + f"{commHlpStrs[i]}"
            # )

        return 0

    def _ext_spec_HELP_HELPER(self, origPth: str, arg: str) \
            -> tuple[str, int]:
        """
        Helper function for _spec_HELP_HELPER(). Displays the help message
        for a specific external command.
        > param origPth: Path of the interpreter
        > return: Tuple of the help string and the error code (0, 107, 108)
                  (ref. src\\errCodes.txt)
        Error code 107:
            No help string available
        Error code 108:
            No such command
        """
        for item in os.scandir(comm.PTHJN(origPth, "bin")):
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

    def _spec_HELP_HELPER(self, origPth: str, arg: str) -> int:
        """
        Displays the help message for a specific command.
        > param origPth: Path of the interpreter
        > param arg: A string to fetch the help string for
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
                if not hasattr(self, arg.upper()):
                    comm.WARN("Command missing but built-in help string " \
                              f"found: '{arg}'",
                              sl=4)
                print(f"COMMAND: {arg.lower()}")
                print('\n'.join(
                    line.expandtabs(4)
                    for line in self.__dict__["help" + arg.upper()]
                ))
                return 0

            tmp = self._ext_spec_HELP_HELPER(origPth, arg)
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

    def HELP(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays the main help messages, and command-specific help messages.
        Error code (0-2, 107, 108) (ref. src\\errCodes.txt)
        Error code 107:
            No help string available
        Error code 108:
            No such command
        """
        optVals   = comm.LOWERLT(opts.values())
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
            err = self._gen_HELP_HELPER(origPth, usageInfo)
        else:
            argsFinIdx = len(args) - 1
            for i, arg in enumerate(args.values()):
                tmp = self._spec_HELP_HELPER(origPth, arg)
                err = err or tmp
                print() if i != argsFinIdx else None

        return err

    def INTRO(self, varTable: dict[str, str], origPth: str, prevErr: int,
              command: str, args: dict[int, str], opts: dict[int, str],
              fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays the intro message.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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
        print(self.interpreter.introTxt)
        return 0

    def PWD(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        print(self.interpreter.path)
        return 0

    def QUIT(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Quits the program.
        Error code (EXIT, 0, 1, 2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def RUNPATH(self, varTable: dict[str, str], origPth: str, prevErr: int,
                command: str, args: dict[int, str], opts: dict[int, str],
                fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays the path Comet is running from.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

        print(origPth)
        return 0

    def set_SET_HELPER(self, args: dict[int, str]) -> int:
        """
        Helper function for the set feature of the set command.
        > param args: Dictionary of arguments
        > return: Error code (0, 1, 105) (ref. src\\errCodes.txt)
        Error code 105:
            Attempted modification of protected variable
        """
        if len(args) != 2:
            comm.ERR("Incorrect format", sl=4)
            return 1

        if comm.LOWERLT(args)[0] == "error":
            comm.ERR("Operation not allowed; cannot edit "
                     "var 'error'", sl=4)
            return 105

        sortedArgs = sorted(args)
        varName    = args[sortedArgs[0]]
        varVal     = args[sortedArgs[1]]
        if keys := comm.DICTSRCH(varName, self.interpreter.varTable,
                                 caseIn=True, returnMode="keys"):
            for key in keys:
                self.interpreter.varTable.pop(key)
        self.interpreter.varTable[varName] = varVal
        return 0

    def rm_SET_HELPER(self, args: dict[int, str]) -> int:
        """
        Helper function for the remove feature of the set command.
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

            if not (keys := comm.DICTSRCH(arg, self.interpreter.varTable,
                                          caseIn=True, returnMode="keys")):
                comm.ERR(f"No such variable: '{arg}'", sl=4)
                err = err or 106
                continue

            for key in keys:
                self.interpreter.varTable.pop(key)

        return err

    def SET(self, varTable: dict[str, str], origPth: str, prevErr: int,
            command: str, args: dict[int, str], opts: dict[int, str],
            fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Sets interpreter variables.
        Error code (0-2, 105, 106) (ref. src\\errCodes.txt)
        Error code 105:
            Attempted modification of protected variable
        Error code 106:
            No such variable
        """
        optVals   = comm.LOWERLT(opts.values())
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
            return self.set_SET_HELPER(args)
        else:
            return self.rm_SET_HELPER(args)

    def STOP(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Pauses the interpreter and waits for user to press any key.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def TIME(self, varTable: dict[str, str], origPth: str, prevErr: int,
             command: str, args: dict[int, str], opts: dict[int, str],
             fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays the current system time.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

    def TIMEIT(self, varTable: dict[str, str], origPth: str, prevErr: int,
               command: str, args: dict[int, str], opts: dict[int, str],
               fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Time the execution of a command.
        Error code (0) (ref. src\\errCodes.txt)
        """
        startTime = ti.default_timer()
        self.interpreter.execute(fullComm.strip().removeprefix(command).strip())
        print(f"elapsed {round(ti.default_timer() - startTime, 6)}s")
        return 0

    def TITLE(self, varTable: dict[str, str], origPth: str, prevErr: int,
              command: str, args: dict[int, str], opts: dict[int, str],
              fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Sets the title of the console window.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
        validOpts = {'h', "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpTITLE))
                return 0

        if not args:
            self.interpreter.title = self.mainFlTitle
        elif len(args) != 1:
            comm.ERR("Incorrect format")
            return 1
        for arg in args.values():
            self.interpreter.title = arg

        ct.windll.kernel32.SetConsoleTitleW(self.interpreter.title)
        return 0

    def VER(self, varTable: dict[str, str], origPth: str, prevErr: int,
            command: str, args: dict[int, str], opts: dict[int, str],
            fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Displays the version of the Comet interpreter.
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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
        print(self.interpreter.version)
        return 0

    def WHEREIS(self, varTable: dict[str, str], origPth: str, prevErr: int,
                command: str, args: dict[int, str], opts: dict[int, str],
                fullComm: str, stream: ty.TextIO, op: str) -> int:
        """
        Error code (0-2) (ref. src\\errCodes.txt)
        """
        optVals   = comm.LOWERLT(opts.values())
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

        builtInComms = [i for i in dir(self.interpreter.builtInComms) if i.isupper()]
        binDir       = comm.PTHJN(origPth, "bin")
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
                modulePath = comm.PTHJN(origPth, "bin",
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
        self.cdtodirs     = self.settings.get("cdtodirs")
        self.execscripts  = self.settings.get("execscripts")
        self.intro        = self.settings.get("intro")
        self.varTable     = {"bookmark": os.path.expanduser('~'),
                             "bm": os.path.expanduser('~'),
                             "error": '0'}
        self.builtInComms = BuiltInComms(self, title)

        if self.path is not None and self.path != '':
            self.path = str(pl.Path(self.path).resolve())
        elif self.path is None or self.path == '':
            self.path = comm.DFLTSETT["path"]
        if self.title is None or self.title == '':
            self.title = title
        if self.cdtodirs is None or self.cdtodirs == '':
            self.cdtodirs = "yes"
        if self.execscripts is None or self.execscripts == '':
            self.execscripts = "yes"
        if self.intro is None or self.intro == '':
            self.intro = "off"
        if self.intro == "on":
            print(self.introTxt)
        elif self.intro != "off":
            comm.WARN("Invalid value for attribute 'intro' in settings file: "
                      f"\"{self.intro}\"", raiser="comet")

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
            for item in os.scandir(comm.PTHJN(self.origPth, "startup")):
                if not os.path.isfile(item):
                    continue
                with open(item) as f:
                    for line in f:
                        self.execute(line.strip('\n'))
        except FileNotFoundError:
            pass
        except PermissionError:
            comm.ERR("Access is denied: "
                     f"\"{comm.PTHJN(self.origPth, "startup")}\";"
                     "Cannot execute startup script(s)")

    def doesPathsExist(self) -> None:
        "Check if the startup path (in the config file) exists."
        if not os.path.isdir(self.path):
            comm.WARN("Startup path does not exist. Using default path",
                      raiser="comet")
            self.path = comm.DFLTSETT["path"]

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
            pass
        elif len(searchResult) > 1:
            comm.ERR("Multiple commands with same name detected; "
                     "possible name conflict between an interpreter "
                     "module and a command file", raiser="comet")
            return 52
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
            return 51

        if spec is None:
            comm.UNERR("Could not get run function",
                       "Could not get run function; Might be due to "
                       "a permission issue or invalid command name")
            return -1
        elif spec.loader is None:
            comm.UNERR("Could not get run function",
                       "Could not get run function; Unknown cause")
            return -1

        func   = 50
        module = None

        try:
            module = ilu.module_from_spec(spec)
            spec.loader.exec_module(module)
            func   = getattr(module, command.upper())

        except (AttributeError, ImportError, FileNotFoundError):
            func = self.aliases[command] if command in self.aliases else func

        except OSError:
            pass

        finally:
            sys.modules = comm.CASEINSENSMODSRCHANDRM(command, sys.modules)
            del module

        return func

    def _before(self) -> None:
        "Called before every execution of execute()"
        pass

    def _after(self) -> None:
        "Called after every execution of execute()"
        pass

    def _shtHndComms_execute(self, command: str, args: dict[int, str],
                             opts: dict[int, str]) -> \
                                tuple[str, dict[int, str], dict[int, str]]:
        """
        Helper function of execute().
        Argument and option handling for shorthand commands (? and !).
        > param command: Command name
        > param args: Dictionary of arguments
        > param opts: Dictionary of options
        > return: Actual command, modified dictionary of arguments and
                  modified dictionary of options
        """
        tempArgs = {}
        tempOpts = {}

        # If there is some non-whitespace characters just after the shorthand
        # commands, insert those characters to arguments or options at the
        # head of the list
        if command[1:]:
            for arg in args:
                tempArgs[arg + 1] = args[arg]
            for opt in opts:
                tempOpts[opt + 1] = opts[opt]
            tempArgs[0] = command[1:]

        return command[0], tempArgs, tempOpts

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
        output   = ''
        pipeOut  = None
        redirOut = None
        parsed   = self.parse(line)
        if parsed == 1:
            return 2

        while parsed:
            args: dict[int, str]
            opts: dict[int, str]
            command, args, opts = parsed.pop(0)
            operation           = ''

            if parsed:
                operation = parsed.pop(0)

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
                tmp     = self._shtHndComms_execute(command, args, opts)
                command = tmp[0]
                args.update(tmp[1])
                opts.update(tmp[2])

            if not command:
                return self.err

            func        = self.getFunc(command)
            capture     = io.StringIO()
            oldStdOut   = sys.__stdout__
            cdtodirs1   = (self.cdtodirs.lower() == "yes"
                           or self.cdtodirs.lower() == "on"
                           or self.cdtodirs == "true")
            cdtodirs2   = (command == '.' or command == ".."
                           or command.endswith('\\') or command.endswith('/'))
            execscripts = (self.execscripts.lower() == "yes"
                           or self.execscripts.lower() == "on"
                           or self.execscripts.lower() == "true")

            if redirOut is not None:
                try:
                    with open(command, 'a') as f:
                        f.write(redirOut)
                except PermissionError:
                    comm.ERR(f"Access is denied: {pl.Path(command).resolve()}",
                            raiser="comet")
                    self.err = 5
                except OSError:
                    comm.ERR("Redirect operation failed; invalid path, disc "
                            "full or unescaped characters?", raiser="comet")
                    self.err = 6
                    return 6
                finally:
                    redirOut = None

            elif isinstance(func, ty.Callable):
                # Output of previous command piped to current command; add
                # the previous ouput to the arguments of current command
                if pipeOut is not None:
                    try:
                        maxPos = max(list(args) + list(opts)) + 1
                    except ValueError:
                        maxPos = 0
                    args[maxPos] = pipeOut

                # Capture the output of current command, to decide its fate
                with cl.redirect_stdout(capture):
                    self.err = func(self.varTable, self.origPth, self.err,
                                    command, args, opts, line, oldStdOut,
                                    operation)

                pipeOut  = None
                redirOut = None
                output   = capture.getvalue()

                if operation != '' and operation not in self.parser.spChars:
                    # TODO: Remove this!
                    comm.ERR(f"Invalid operation: '{operation}'", raiser="comet")
                    return self.err

                # Includes operation == ''
                if operation in "^&;":
                    print(output, end='')
                    if operation == '&' and self.err:
                        return self.err
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

            elif execscripts and os.path.isfile(command):
                err = 0
                try:
                    with open(command) as f:
                        for line in f:
                            tmp = self.execute(line.removesuffix('\n'),
                                               before=before, after=after)
                            err = err or tmp
                        self.err = err
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

            elif (cdtodirs1 and cdtodirs2 and os.path.isdir(command)):
                if args or opts:
                    argsAndOpts = args and opts
                    self.err    = 53
                    comm.ERR(f"No {"arguments" if args else ''}"
                             f"{" or " if argsAndOpts else ''}"
                             f"{"options" if opts else ''} allowed here",
                             raiser="comet")
                    return 1
                self.builtInComms.CD(self.varTable, self.origPth, self.err,
                                     "cd", {0: command}, {}, line, oldStdOut,
                                     operation)

            else:
                self.err = func
                if func == 50:
                    comm.ERR(f"Bad command: \"{command}\"", raiser="comet")
                if func == 51:
                    comm.ERR("Command too long", raiser="comet")

        self._after() if after else None
        self.varTable["error"] = str(self.err)
        return 0
