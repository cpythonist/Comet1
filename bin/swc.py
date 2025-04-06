#
# Comet 1 standard library command
# Filename: src\\bin\\swc.py
# Copyright (c) 2025, Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licensed under the Apache-2.0 License.
#

import os
import sys
import typing  as ty

# Add src\\core to sys.path
srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import commons as comm
sys.path.pop(1)

helpStr = (
    "Calculate word count, line count, and byte count.", '',
    "USAGE: wc [-h] [-c] [-w] [-l] (str | -f file)", '', "ARGUMENTS", "str",
    "\tString to be analysed", "file", "\tFile to be analysed", '',
    "OPTIONS", "-c / --chars", "\tCount characters", "-f / --file",
    "-h / --help", "\tHelp message", "-l / --lines", "\tCount lines",
    "-w / --words", "\tCount words",
)


def HELPER_WC(data: str, chars: bool, words: bool, lines: bool) -> list[str]:
    """
    Helper function to calculate word count, line count, and byte count.
    > param data: String to be analysed
    > param chars: Count characters
    > param words: Count words
    > param lines: Count lines
    > return: List of strings containing word count, line count, and byte count
    """
    toPrint = []
    if chars:
        toPrint.append(f"c: {len(data)}")
    if words:
        toPrint.append(f"w: {len(data.split())}")
    if lines:
        toPrint.append(f"l: {len(data.split('\n'))}")
    return toPrint


def WC(varTable: dict[str, str], origPth: str, prevErr: int, command: str,
       args: dict[int, str], opts: dict[int, str], fullComm: str,
       stream: ty.TextIO, op: str) -> int:
    """
    Checks for the existance of a path.
    > param varTable: Variable table
    > param origPth: Path to the interpreter
    > param prevErr: Previous error code
    > param command: Name of the command
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full command
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code () (ref. src\\errCodes.txt)
    """
    optVals    = comm.LOWERLT(opts.values())
    validOpts  = {'c', 'f', 'l', 'w', 'h',
                  "-chars", "-file", "-lines", "-words", "-help"}
    chars      = False
    words      = False
    lines      = False
    isFl       = False
    toPrint    = []

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0
        for pos in opts:
            opt = opts[pos].lower()
            if opt == 'c' or opt == "-chars":
                chars = True
            elif opt == 'l' or opt == "-lines":
                lines = True
            elif opt == 'w' or opt == "-words":
                words = True
            elif opt == 'f' or opt == "-file":
                if isFl:
                    comm.ERR(f"Cannot accept multiple files: -{opt}")
                    return 3
                if pos + 1 not in args:
                    comm.ERR(f"Missing argument for -{opt}: file")
                    return 3
                txtOrFl = args[pos + 1]
                isFl    = True
    
    if not chars and not words and not lines:
        chars = True
        words = True
        lines = True

    if not args or len(args) != 1:
        comm.ERR("Incorrect format")
        return 1

    if 'f' not in optVals and "-file" not in optVals:
        txtOrFl = args[sorted(args)[0]]

    if isFl:
        if not os.path.isfile(txtOrFl):
            comm.ERR(f"No such file: \"{txtOrFl}\"")
            return 4
        try:
            with open(txtOrFl, buffering=1) as f:
                data = f.read()
        except PermissionError:
            comm.ERR(f"Access is denied: \"{txtOrFl}\"")
            return 5
        except UnicodeDecodeError:
            comm.ERR(f"Cannot decode file: \"{txtOrFl}\"")
            return 9

    else:
        data = txtOrFl

    toPrint = HELPER_WC(data, chars, words, lines)
    print("; ".join(toPrint))
    return 0
