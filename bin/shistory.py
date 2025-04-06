#
# Comet 1 standard library command
# Filename: src\\bin\\shistory.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import subprocess as sp
import typing     as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = ("Displays the history of the program.", '', "USAGE: history [-h]",
           '', "OPTION(S)", "-h / --help", "\tHelp message")
history = (
    "The Second interpreter was written by CPythonist in late 2020.",
    '', "The first implementation of the interpreter was very basic, "
        "but could not be continued as after running the 'time' command "
        "(which gives a live clock and interrupting it with ^C would stop "
        "the clock), the interpreter would crash if ^C was repeated pressed "
        "or other specific activities.",
    '', "The actual first version, Second-1.0, was first implemented in 2021. "
        "Second-1.0 had extremely basic parsing abilities, and could only "
        "input a command, then get the arguments in a separate input prompt, "
        "so it had multiple prompts for one command.", '',
    "Second-2.0 followed with the same parser with added features (new "
    "commands) to the interpreter.", '',
    "Second-3.0 was made in 2023 and had an upgraded CPython interpreter - "
    "version 3.9.6. Second 3 had enormously advanced parsing compared to the "
    "previous two versions. All arguments and options can be entered on the "
    "same line, but each argument and option was required to have quotes "
    "around them, and only one type of quote symbol can be used in a single "
    "command.", '', "Second-4.0 was made in 2024. Second 4 removed the need "
                    "for quotes, but could only perform operations if the "
                    "quotes, if used (in cases were quoted arguments are "
                    "needed, for example, when a directory name has spaces) "
                    "were of a single type.", '',
    "Second-5.0, was made in 2024. It has major upgrades to parsing and "
    "provides far more powerful and flexible commands such as allowing "
    "variable number of arguments to a command.", '',
    "Clash 1 was started in 2024, just after Second-5.0 and finished in 2025. "
    "It featured a several new commands, with greater parsing abilities, "
    "being able to parse and execute commands inside commands (like "
    "\"echo '`ls`'\"), adding features for piping, redirection and running "
    "multiple commands in the same line.", '',
    "For more information, please visit to "
    "http://cpythonist.github.io/clash.html."
)


def HISTORY(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
            args: dict[int, str], opts: dict[int, str], fullComm: str,
            stream: ty.TextIO, op: str) -> int:
    """
    Displays the history of the program.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2) (ref. src\\errCodes.txt)
    """
    copy      = False
    optVals   = opts.values()
    validOpts = {'c', 'h', "-copy", "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt in ('c', '-copy'):
                copy = True

    if args:
        comm.ERR("Incorrect format")
        return 1

    print(tmp := '\n'.join(history))
    if copy:
        sp.run(["clip.exe"], input=tmp.encode("utf-8"), check=True)

    return 0
