#
# Comet 1 source code
# Infinite Inc.
# Copyright (c) 2025 Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename: src\\core\\parser.py
# Description: Contains the parser for the interpreter
#

import io
import sys
import contextlib as cl
import typing     as ty
import commons    as comm
if ty.TYPE_CHECKING:
    import comet


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
            '`': 105,
            # '@': 106
            # '<': -1
        }
        self.escChars = {
            "\\\\": '\\',
            "\\\"": '"',
            "\\'" : '\'',
            "\\n" : '\n',
        }

        self.ERR_NOSUCHVAR = 2

        self._rdChar()

    def setIntrp(self, intrp: "comet.Intrp") -> None:
        self.intrp = intrp

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

    def _rdUnquotedArg(self) -> str:
        """
        Read an unquoted argument.
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
                elif self.char == 't':
                    self.src = self.src[:self.pos-1] + '\t' + self.src[self.pos+1:]
                elif self.char == 'r':
                    self.src = self.src[:self.pos-1] + '\r' + self.src[self.pos+1:]
                elif self.char == '"':
                    self.src = self.src[:self.pos-1] + '"' + self.src[self.pos+1:]
                elif self.char == '\'':
                    self.src = self.src[:self.pos-1] + '\'' + self.src[self.pos+1:]
                elif self.char == '`':
                    self.src = self.src[:self.pos-1] + '`' + self.src[self.pos+1:]
                self.pos -= 1

            self._rdChar()

        return self.src[startPos:self.pos]

    def _rdQuotedCommOrArg(self, quote: str) -> str | int:
        """
        Read a quoted command/argument.
        > param quote: The quote character
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
                elif self.char == 't':
                    self.src = self.src[:self.pos-1] + '\t' + self.src[self.pos+1:]
                elif self.char == 'r':
                    self.src = self.src[:self.pos-1] + '\r' + self.src[self.pos+1:]
                elif self.char == '"':
                    self.src = self.src[:self.pos-1] + '"' + self.src[self.pos+1:]
                elif self.char == '\'':
                    self.src = self.src[:self.pos-1] + '\'' + self.src[self.pos+1:]
                elif self.char == '`':
                    self.src = self.src[:self.pos-1] + '`' + self.src[self.pos+1:]
                self.pos -= 1

            self._rdChar()

        return self.src[startPos+1:self.pos]

    def _rdOpt(self) -> str:
        """
        > return: The parsed option
        """
        stPos = self.pos
        self._rdChar()

        while not self.char.isspace() and self.char not in self.spChars:
            if self.char == '\0':
                return self.src[stPos+1:self.pos+1]
            self._rdChar()

        return self.src[stPos+1:self.pos]

    def _rdComm(self) -> str | int:
        """
        Read the command name in the input line.
        > return: The parsed quoted argument or integer error code
            1: Unexpected end of line while parsing the quoted command, i.e.
               missing closing quote
        """
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

    def _evalCommands(self, line: str) -> tuple[str, int]:
        """
        Execute commands.
        """
        capture   = io.StringIO()

        with cl.redirect_stdout(capture):
            err = self.intrp.execute(line)

        if err == 0:
            return capture.getvalue(), err

        return '', err

    def parse(self, varTable: dict[str, str]) \
            -> list[tuple[str, dict[int, str], dict[int, str]] | str] | int:
        """
        Parse the source string present in self.src.
        > param varTable: Variable table
        > return: List of tuple of command, arguments, options, separated by
                  strings representing various operations, or an integer error
                  code (ref. src\\errCodes.txt)
        """
        args   : dict[int, str]
        opts   : dict[int, str]
        command: str | int
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
        if isinstance(command, int):
            if command == 1:
                comm.ERR("Unclosed quoted command", raiser='c')
                return comm.ERR_UNCLOSEDQUOTEDCMD
            # Fatal unhandled case
            return comm.ERR_UNKNOWN

        while self.char != '\0':
            if self.char.isspace():
                self._rdChar()
                continue

            # Subcmd evaluation
            if self.char == '`':
                res = self._rdQuotedCommOrArg('`')
                if isinstance(res, int):
                    if res == 1:
                        comm.ERR("Unclosed subcommand", raiser='c')
                        return comm.ERR_UNCLOSEDSUBCMD
                    # Fatal unhandled case
                    return comm.ERR_UNKNOWN

                if self.char == '`':
                    self._rdChar()

                output, err = self._evalCommands(res)
                if err:
                    comm.ERR("Subcommand execution failed", raiser='c')
                    return comm.ERR_SUBCMDEXECFAILED

                args[count] = output

            # Var access
            elif self.char == '@':
                res = self._rdQuotedCommOrArg('@')
                if isinstance(res, int):
                    if res == 1:
                        comm.ERR("Unclosed variable name", raiser='c')
                        return comm.ERR_UNCLOSEDVARNM

                if self.char == '@':
                    self._rdChar()

                matches = comm.DICTSRCH(res, varTable, caseIn=True)
                if not matches:
                    comm.ERR(f"No such variable: '{res}'")
                    return comm.ERR_NOSUCHINTPRVAR
                elif len(matches) > 1:
                    comm.UNERR("That's not supposed to happen... WE GOT MORE "
                               "THAN ONE MATCH WHILE SEARCHING FOR THE "
                               "VARIABLE!", raiser='c')
                    return comm.ERR_UNKNOWN

                args[count] = matches[0]

            # Operations like piping, redirn, cmd separation, etc.
            elif self.char in self.spChars:
                curSpChar   = self.char
                self.src    = self.src[self.pos+1:]

                subCmdParse = self.parse(varTable)
                if isinstance(subCmdParse, int):
                    return subCmdParse

                full += [(command, args, opts), curSpChar, *subCmdParse]
                return full

            # Quoted args
            if (temp := (self.char == '\'')) or self.char ==  '"':
                arg = self._rdQuotedCommOrArg('\'' if temp else '"')
                if isinstance(arg, int):
                    if arg == 1:
                        comm.ERR("Unclosed quoted argument", raiser='c')
                        return comm.ERR_UNCLOSEDQUOTEDARG
                    # Fatal unhandled case
                    return comm.ERR_UNKNOWN
                args[count] = arg

            # Opts
            elif self.char == '-' and not self._pkChar().isspace() \
                    and self._pkChar() != '\0':
                opt         = self._rdOpt()
                opts[count] = opt

            # Unquoted args
            elif self.char not in (' ', '\0'):
                arg         = self._rdUnquotedArg()
                args[count] = arg

            # Needs to be repeated even though same block is present above,
            # to account for cases such as when sp char is present just after
            # an opt without any whitespace, etc.
            if self.char in self.spChars:
                curSpChar      = self.char
                self.src       = self.src[self.pos+1:]

                otherCmdsParse = self.parse(varTable)
                if isinstance(otherCmdsParse, int):
                    return otherCmdsParse

                full += [(command, args, opts), curSpChar, *otherCmdsParse]
                return full

            count += 1
            self._rdChar()

        full.append((command, args, opts))
        return full
