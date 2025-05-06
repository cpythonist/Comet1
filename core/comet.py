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
import types
import contextlib     as cl
import ctypes         as ct
import importlib.util as ilu
import pathlib        as pl
import typing         as ty
import builtInCmds    as bic
import commons        as comm
import parser         as par


# This annotation is too damn long to be used directly multiple times;
# annotation for a command function
funcTypeAnnot = ty.Callable[
    [
        dict[str, str], str, int, str, dict[int, str], dict[int, str],
        str, ty.TextIO, str, bool
    ],
    int
]


class Intrp:
    def __init__(self, parser: par.Parser, settings: dict[str, str],
                 title: str, mainProgArgs: dict[str, ty.Any]) -> None:
        self.varTable: dict[str, str]
        self.aliases : dict[str, str]

        self.introTxt     = comm.DECOMPSTR(b"x\x9cs\xce\xcfM-Q0\xd43\xe0\xf2\xc9LN\xcdKN\xb5Rp,HL\xceH\xd55\x02\x8a\xb9\xe4\xe7\xa9\x97(\xa4\xe5\x17\xa5\x03\x15%&\xe5\x97\x96(\x94d\xa4*\xa4\x16''\x16\xa4*\x14\xa7\x16\x96\x82\xb4\x14+\x02\x00\x16L\x17e")
        self.version      = 1.0
        self.parser       = parser
        self.settings     = settings
        self.origPth      = comm.ORIGPTH
        self.varTable     = {"error"  : '0',
                             "prevpth": '.',
                             "ud"     : comm.USRDIR,
                             "rp"     : comm.ORIGPTH}
        self.title        = self.settings.get("title", '')
        self.title        = self.title or title
        self.builtInCmds  = bic.BuiltInCmds(self, self.title)
        self.lastCmd      = ''
        self.err          = 0
        self.mainProgArgs = mainProgArgs
        self.debug        = self.mainProgArgs["debug"]
        self.cache        = {}

        self.shortHandCmds = {'?': "help", '!': "cmd"}

        self.detPth()
        self.detCdToDirs()
        self.detExecScripts()
        self.detIntro()
        self.detCache()

        os.chdir(self.path)
        ct.windll.kernel32.SetConsoleTitleW(self.title)

        self.aliases = {}
        loadErr = self.loadAliases()
        if loadErr:
            comm.ERR("Could not load aliases")
        self.lAliases = [i.lower() for i in self.aliases]

        execErr = self.runStartupScripts()
        if execErr:
            comm.ERR("Issues encountered with startup scripts")

    def detPth(self) -> None:
        """
        Determine the parameter path's value.
        """
        self.path = self.mainProgArgs.get("workingdirectory", '')

        if not self.path or not os.path.isdir(self.path):
            # Path is supplied and does not exist
            if self.path is not None:
                comm.ERR("Path supplied does not exist", raiser='c')
            self.path = self.settings.get("path")

        if not self.path or not os.path.isdir(self.path):
            comm.ERR(f"Startup path does not exist", raiser='c')
            self.path = comm.DFLTSETT["path"]

        self.path = str(pl.Path(self.path).resolve())

    def detCdToDirs(self) -> None:
        """
        Determine the parameter cdtodirs's value.
        """
        self.cdtodirs = self.settings.get("cdtodirs", '')

        if (not self.cdtodirs or self.cdtodirs == "yes"
            or self.cdtodirs == "true" or self.cdtodirs == "on"):
            self.cdtodirs = "true"
        elif (self.cdtodirs == "no" or self.cdtodirs == "false"
              or self.cdtodirs == "off"):
            self.cdtodirs = "false"
        else:
            comm.ERR(f"(SETTINGS) Invalid value for 'cdtodirs': '{self.cdtodirs}'",
                     raiser='c')
            self.cdtodirs = "true"

    def detExecScripts(self) -> None:
        """
        Determine the parameter execscripts's value.
        """
        self.execscripts = self.settings.get("execscripts", '')

        if not self.execscripts or self.execscripts in ("true", "yes", "on"):
            self.execscripts = "true"
        elif self.execscripts in ("false", "no", "off"):
            self.execscripts = "false"
        else:
            comm.ERR(f"(SETTINGS) Invalid value for 'execscripts': '{self.execscripts}'",
                     raiser='c')
            self.execscripts = "true"

    def detIntro(self) -> None:
        """
        Determine the parameter intro's value.
        """
        self.intro = self.settings.get("intro", '')

        if not self.intro or self.intro in ("true", "yes", "on"):
            self.intro = "true"
            print(self.introTxt)
        elif self.intro in ("false", "no", "off"):
            self.intro = "false"
        else:
            comm.ERR(f"(SETTINGS) Invalid value for 'intro': '{self.intro}'",
                     raiser='c')
            self.intro = "true"

    def detCache(self) -> None:
        """
        Determine the parameter cache's value.
        """
        self.writeCache = self.settings.get("cache", '')

        if not self.writeCache or self.writeCache in ("true", "yes", "on"):
            self.writeCache = "true"
        elif self.writeCache in ("false", "no", "off"):
            self.writeCache = "false"
        else:
            comm.ERR(f"(SETTINGS) Invalid value for 'intro': '{self.writeCache}'",
                     raiser='c')
            self.writeCache = "true"

    def loadAliases(self) -> int:
        """
        Load aliases from _aliases.txt.
        > return: Error code (ref. src\\errCodes.txt)
        """
        try:
            with open(os.path.join(self.origPth, "_aliases.txt"),
                      buffering=1) as f:
                for i, ln in enumerate(f):
                    alias, sep, value = ln.partition('=')
                    if sep == '':
                        comm.ERR(f"(ALIASES) Cannot parse line {i + 1}: \"{ln}\"",
                                 raiser='c')
                        continue
                    if not comm.PARAMOK(alias):
                        comm.ERR(f"(ALIASES) Invalid name on line {i + 1}: '{alias}'",
                                 raiser='c')
                        continue
                    self.aliases[alias] = value.removesuffix('\n')

        except FileNotFoundError:
            try:
                open(os.path.join(self.origPth, "_aliases.txt"), 'w').close()
            except PermissionError:
                comm.ERR("(ALIASES) Access is denied; unable to create file",
                         raiser='c')
                return comm.ERR_PERMDENIED

        except PermissionError:
            comm.ERR("(ALIASES) Access is denied to write to file", raiser='c')
            return comm.ERR_PERMDENIED

        return comm.ERR_SUCCESS

    def runStartupScripts(self) -> int:
        """
        Execute startup scripts.
        > return: Error code (ref. src\\errCodes.txt)
        """
        pth = os.path.join(self.origPth, "startup")
        err = comm.ERR_SUCCESS

        try:
            for item in os.scandir(pth):
                if not os.path.isfile(item):
                    continue
                try:
                    with open(item) as f:
                        for line in f:
                            self.execute(line.strip('\n'))
                except FileNotFoundError:
                    pass
                except PermissionError:
                    comm.ERR(f"Access is denied: Cannot execute \"{item.name}\"")
                    err = err or comm.ERR_SUCCESS

        except FileNotFoundError:
            pass

        except PermissionError:
            comm.ERR(f"Access is denied: \"{pth}\"; Cannot execute startup script(s)")
            err = err or comm.ERR_SUCCESS

        return err

    def setErrCode(self, code: int) -> int:
        """
        > return: Error code (for this function)
            Return codes
            0: Success
            1: Could not set error code (type mismatch)
        """
        if not isinstance(code, int):
            comm.CRIT(f"Non-integer return code received: {code}, {type(code)}", raiser='c')
            return 1

        self.err = code

        matches = comm.DICTSRCH("error", self.varTable, caseIn=True, returnMode="keys")
        if matches:
            self.varTable[matches[0]] = str(code)
        else:
            self.varTable["error"] = str(code)

        return 0

    def parse(self, line: str) -> \
            list[tuple[str, dict[int, str], dict[int, str]] | str]:
        """
        Parse an input line.
        > param line: Full input line to be parsed
        > return: Parsed output; please refer to the parser module for more
                  information
        """
        self.parser.src = line
        return self.parser.parse(self.varTable)

    def loadMod(self, cmd: str) -> tuple[types.ModuleType | None, int]:
        """
        Load a module from the "bin" directory.
        > param cmd: Command name
        > return: Module or None, and error code (ref. src\\errCodes.txt)
        """
        cmdPyPth  = os.path.join(self.origPth, "bin", cmd.lower() + ".py")
        cmdPydPth = os.path.join(self.origPth, "bin", cmd.lower() + ".pyd")
        cmdPth    = cmdPyPth if os.path.exists(cmdPyPth) else cmdPydPth

        if not os.path.exists(cmdPth):
            return None, comm.ERR_SUCCESS

        spec = ilu.spec_from_file_location(cmd, cmdPth)
        if spec is None or spec.loader is None:
            return None, comm.ERR_UNKNOWN

        mod = ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, comm.ERR_SUCCESS

    def getFunc(self, cmd: str) -> tuple[funcTypeAnnot, int] | int | None:
        """
        Get the function to be called from the modules in directory "src\\bin".
        > param cmd: Command name
        > return: A function object (if everything went well), an integer
                  error code (if something started acting up) or None (if
                  the function is not found)
        """
        func = comm.ERR_BADCOMM
        mod  = None

        res = comm.DICTSRCH(cmd, self.cache, caseIn=True)
        if res:
            # Not None and contains atleast one element
            return res[0]

        if hasattr(self.builtInCmds, cmd.upper()):
            func = getattr(self.builtInCmds, cmd.upper())
            return func

        try:
            mod, _ = self.loadMod(cmd)

            func = getattr(mod, cmd.upper())

        except (AttributeError, ImportError, FileNotFoundError):
            for alias in self.aliases:
                if alias.lower() == cmd.lower():
                    func = self.aliases[cmd]
                    break

        except ValueError:
            # Raised if path is too long
            return comm.ERR_CMDTOOLONG

        except OSError:
            pass

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

    def _redir_execute_HELPER(self, command: str, redirOut: str) -> int:
        err = comm.ERR_SUCCESS

        try:
            with open(command, 'a') as f:
                f.write(redirOut)
        except PermissionError:
            comm.ERR(f"Is a directory or access is denied: "
                     f"\"{pl.Path(command).resolve()}\"", raiser='c')
            err = comm.ERR_PERMDENIED
        except OSError:
            comm.ERR("Redirect operation failed; invalid path, disc "
                        "full or unescaped characters?", raiser='c')
            err = comm.ERR_OSERR

        return err

    def _call_execute_HELPER(
            self, func: funcTypeAnnot, command: str, args: dict[int, str],
            opts: dict[int, str], line: str, oldStdOut, op: str, pipeOut: str,
            capture: ty.TextIO
        ) -> tuple[ty.TextIO, int]:

        # o/p of previous cmd piped to current cmd; add prev o/p to args of
        # current cmd
        if pipeOut is not None:
            try:
                maxPos = max(list(args) + list(opts)) + 1
            except ValueError:
                maxPos = 0
            args[maxPos] = pipeOut

        # Capture o/p of current cmd, to decide its fate
        with cl.redirect_stdout(capture):
            err = func(self.varTable, self.origPth, self.err, command,
                       args, opts, line, oldStdOut, op, self.debug)

        return capture, err

    def execute(self, line: str, before: bool = True, after: bool = True) -> int:
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
        > param setLastCmd: Set last executed command
        > return: Integer error code (ref. src\\errCodes.txt)
        """
        self._before() if before else None
        output   = ''
        pipeOut  = None
        redirOut = None
        parsed   = self.parse(line)
        err      = comm.ERR_SUCCESS
        comm.DEBUG(f"Parsed input line: {parsed}") if self.debug else None

        if isinstance(parsed, int):
            return parsed

        while parsed:
            args: dict[int, str]
            opts: dict[int, str]
            tmp = parsed.pop(0)
            if isinstance(tmp, str):
                comm.UNERR(f"That is not supposed to happen. First element after parsing is of type {type(tmp)}",
                           raiser='c')
                return comm.ERR_UNKNOWN
            (cmd, args, opts), op = (tmp), ''

            if parsed:
                if not isinstance(tmp := parsed.pop(0), str):
                    comm.UNERR(f"That is not supposed to happen. Pop from list for operation is of type {type(tmp)}",
                               raiser='c')
                    return comm.ERR_UNKNOWN
                op = tmp

            if self.debug:
                comm.DEBUG("Initial command, arguments, options and operation: "
                           f"'{cmd}', {args}, {opts} and '{op}'")

            if not cmd:
                return self.err

            if len(cmd) == 1 and ord(cmd) in (26, 4):
                # Ughhh. Will be caught in the main module
                raise EOFError

            # Same as in Bash
            if cmd == "$?" and not args and not opts:
                print(self.err)
                return self.err

            # ^Z in args
            if [i for i in args if len(args[i]) == 1 and ord(args[i]) == 26]:
                return self.err

            # -^Z in opts
            if [i for i in opts if len(opts[i]) == 1 and ord(opts[i]) == 26]:
                return self.err

            if cmd.startswith(('!', '?')):
                tmp = self._shtHndComms_execute(cmd, args, opts)
                cmd = self.shortHandCmds[tmp[0]]
                args.update(tmp[1])
                opts.update(tmp[2])
                if self.debug:
                    comm.DEBUG("Updated command, arguments, options and "
                               f"operation: '{cmd}', {args}, {opts} and "
                               f"'{op}'")

            func      = self.getFunc(cmd)
            capture   = io.StringIO()
            oldStdOut = sys.__stdout__

            # Redirect output
            if redirOut is not None:
                if self.debug:
                    comm.DEBUG("Redirection block executing")
                tmp      = self._redir_execute_HELPER(cmd, redirOut)
                err      = err or tmp
                redirOut = None

            # Execute a command function
            elif isinstance(func, ty.Callable):
                if self.debug:
                    comm.DEBUG("Command block executing")

                capture, err = self._call_execute_HELPER(
                    func, cmd, args, opts, line, oldStdOut, op, pipeOut, capture
                )

                res = comm.DICTSRCH(cmd, self.cache, caseIn=True)
                if self.writeCache == "true" and not res:
                    self.cache[cmd] = func

                pipeOut  = None
                redirOut = None
                output   = capture.getvalue()

                if op in ('', '^', '&', ';'):
                    print(output, end='')
                    if op == '&' and err:
                        return err
                elif op == '|':
                    if err:
                        return err
                    pipeOut = output
                elif op == '>':
                    redirOut = output

            # Execute an alias
            elif isinstance(func, str):
                if self.debug:
                    comm.DEBUG("Alias block is executing...")

                tempOptDict: dict[int, str] = {}
                for arg in args:
                    args[arg] = '"' + args[arg] + '"'
                for opt in opts:
                    tempOptDict[opt] = '-' + opts[opt]

                args.update(tempOptDict)
                consCmd = f"{func} {' '.join(args.values())}"
                tmp     = self.execute(consCmd, before=False)
                err     = err or tmp

            # Execute a script on passing fl name instead of a cmd
            elif os.path.isfile(cmd):
                if self.debug:
                    comm.DEBUG("Script exection block executing")

                if self.execscripts != "true":
                    comm.ERR(f"Is a file: \"{cmd}\"", raiser='c')
                    err = err or comm.ERR_ISAFL
                else:
                    try:
                        with open(cmd) as f:
                            for line in f:
                                tmp2 = self.execute(line.removesuffix('\n'),
                                                   before=before, after=after)
                                err  = err or tmp2
                    except UnicodeDecodeError:
                        comm.ERR("Does not appear to contain valid UTF-8: "
                                f"\"{pl.Path(cmd).resolve()}\"",
                                raiser='c')
                        err = err or comm.ERR_CANTDECODE
                    except PermissionError:
                        comm.ERR("Access is denied: "
                                f"\"{pl.Path(cmd).resolve()}\"",
                                raiser='c')
                        err = err or comm.ERR_PERMDENIED

            # Change dir on passing dir name instead of a cmd
            elif os.path.isdir(cmd):
                if self.debug:
                        comm.DEBUG("Change directory block executing")

                if self.cdtodirs != "true":
                    comm.ERR(f"Is a directory: \"{cmd}\"", raiser='c')
                    err = err or comm.ERR_ISADIR
                else:
                    if args or opts:
                        argsAndOpts = args and opts
                        err         = err or comm.ERR_INVUSEOFINTPR
                        comm.ERR("No {}{}{} allowed here".format(
                            "arguments" if args else '',
                            " or " if argsAndOpts else '',
                            "options" if opts else ''
                        ), raiser='c')
                    else:
                        tmp3 = self.execute(f"cd \"{comm.CREPR(cmd)}\"")
                        err  = err or tmp3

            # Else, BOOM!
            else:
                if self.debug:
                    comm.DEBUG("Error block executing")
                if func is None:
                    func = comm.ERR_BADCOMM

                err = func
                if func == comm.ERR_UNKNOWN:
                    comm.ERR(f"Unknown command: \"{cmd}\"", raiser='c')
                if func == comm.ERR_BADCOMM:
                    comm.ERR(f"Bad command: \"{cmd}\"", raiser='c')
                if func == comm.ERR_CMDTOOLONG:
                    comm.ERR("Command too long", raiser='c')
                if op in ('&', '>'):
                    break

        self.lastCmd = line
        self._after() if after else None
        return err
