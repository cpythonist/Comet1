#
# Comet 1 standard library command
# Filename: bin\\stree.py
# Copyright (c) 2024, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import pathlib as pl
import typing  as ty

# Add directory "src\\core" to list variable sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays a tree of all subdirectories (and files) in a directory.",
    "USAGE: tree [-h] [-f] [-b | -y | -i] [dir ...]", "ARGUMENT(S)",
    "\tNONE", "\t\tCurrent working directory shall be used", "\tdir",
    "\t\tDirectory(ies) which need to be 'tree'-ed",
    "OPTION(S)", "\tNONE", "\t\tBatch output", "\t-b / --batch",
    "\t\tBatch output", "\t-f / --files", "\t\tPrint files",
    "\t-h / --help", "\t\tHelp message", "\t-i / --incremental",
    "\t\tIncremental output", "\t-y / --hybrid", "\t\tHybrid (buffered) output"
)


def TREE(interpreter: comet.Interpreter, command: str, args: dict[int, str],
         opts: dict[int, str], fullComm: str, stream: ty.TextIO,
         op: str) -> int:
    """
    Displays a tree of all subdirectories (and files) inside a directory.
    > param interpreter: Interpreter object
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (-1, 0, 2-4, 7) (ref. src\\errCodes.txt)
    """
    # For printing files
    optVals    = comm.lowerLT(opts.values())
    validOpts  = {'f', 'b', 'y', 'i', 'h',
                  "-files", "-batch", "-hybrid", "-incremental", "-help"}
    printFiles = False
    mode       = ''

    if not args:
        args = {-1: os.getcwd()}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for opt in optVals:
            if opt == 'f' or opt == '-files':
                printFiles = True
                continue
            if mode:
                comm.ERR("Cannot use more than one mode")
                return 3
            if opt == 'y' or opt == '-hybrid':
                mode = "hybrid"
            elif opt == 'i' or opt == '-incremental':
                mode = "incremental"
            elif opt == 'b' or opt == '-batch':
                mode = "batch"

    for arg in args.values():
        path      = str(pl.Path(arg).resolve())
        count     = 0
        # Find dir lvl in file structure
        levelArgs = path.count(os.sep)
        if not os.path.isdir(path):
            comm.ERR(f"No such directory: \"{path}\"")
            return 4

        buffer: list[str]
        buffer       = []
        bufferAppend = buffer.append
        if not mode or mode == "batch":
            func = sys.stdout.write
        elif mode == "hybrid":
            func = bufferAppend
        elif mode == "incremental":
            func = stream.write
        else:
            comm.UNERR("Unknown mode; not supposed to happen. Please "
                       "report to the developers", comm.GETEXC())
            return -1

        func(path + ":")

        try:
            for root, _, files in os.walk(path):
                level         = (str(pl.Path(root).resolve()).count(os.sep)
                                    - levelArgs)
                fillIndent    = ' ' * 4 * (level - 1) + '├' + "───"
                fillSubindent = ' ' * 4 * (level) + '├' + "───"
                func((f"{fillIndent}{os.path.basename(root)}"
                        f"{os.sep}" if count else '') + '\n')
                if printFiles:
                    for file in files:
                        func(f"{fillSubindent}{os.path.basename(file)}" + '\n')
                count += 1
                if mode == "hybrid" and count % 1000 == 0:
                    stream.write(''.join(buffer))
                    buffer.clear()

        except FileNotFoundError:
            comm.ERR("Race condition: directory modified before "
                     f"{command.lower()} executed")
            return 7

        if buffer and mode == "hybrid":
            stream.write(''.join(buffer))

    return 0
