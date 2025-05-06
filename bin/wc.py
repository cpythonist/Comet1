#
# Comet 1 standard library command
# Filename: src\\bin\\wc.py
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

helpStr = b"x\x9c]\x90\xbb\x0e\x820\x14\x86g\xceS\x9cQ\x13\xab\xbb\x1b!x\x19\x04ca2\x0c\xa5\x94KR\xc1\xb4%\x84\xc4\x87\xb7\xad\xca\xe0\xf2\xe5\xfc\xfd\x9a\xbf\x97\x88I>Jf\x04N\x83\xaa\x90\x0fco6(\xbb^\xfcf\xd6WX\xce\xe6\x9b\xb7\x009\r\x8f\xf1\x1e\'\x8ew\xd2\x16\x16\xdcar\x90\x05\xae\xb4Q\xf8BRc\xddI\xb1\x06\x08o\xc7\xfc\x12\'\x19\x05k \xa0Fu}\x83f\xc0R\xd8n&g-*p{!8X\xfe\x1bH\xaf\xd99M(\x10\x8e;$\x84\xb7Li\x08\"w\x19t\x81q#\xec\x8a=\xd0i_DZ?\xb7B>!8Y\xe2Ch\xcd\x1ak\xa47\xee}K\xc9\'\x90\xc9\x1b\xf7\x0b\x8b\xf1\xe1\r2\x8bZt"


def HELPER_WC(data: str, chars: bool, words: bool, lines: bool) -> list[str]:
    """
    Helper function to calculate word count, line count, and byte count.
    > param data: String to be analysed
    > param bytes_: Count bytes
    > param words: Count words
    > param lines: Count lines
    > return: List of strings containing word count, line count, and byte count
    """
    toPrint = []
    if chars:
        toPrint.append(f"b: {len(data.encode())}")
    if words:
        toPrint.append(f"w: {len(data.split())}")
    if lines:
        toPrint.append(f"l: {len(data.split('\n'))}")
    return toPrint


def WC(varTable: dict[str, str], origPth: str, prevErr: int, cmd: str,
       args: dict[int, str], opts: dict[int, str], fullCmd: str,
       stream: ty.TextIO, op: str, debug: bool) -> int:
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
    > param debug: Is debugging enabled?
    > return: Error code (ref. src\\errCodes.txt)
    """
    optVals    = comm.LOWERLT(opts.values())
    validOpts  = {'b', 'f', 'l', 'w', 'h',
                  "-bytes", "-file", "-lines", "-words", "-help"}
    bytes_     = False
    words      = False
    lines      = False
    isFl       = False
    toPrint    = []

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.DECOMPSTR(helpStr))
            return comm.ERR_SUCCESS

        for pos in opts:
            opt = opts[pos].lower()
            if opt == 'b' or opt == "-bytes":
                bytes_ = True
            elif opt == 'l' or opt == "-lines":
                lines = True
            elif opt == 'w' or opt == "-words":
                words = True
            elif opt == 'f' or opt == "-file":
                if isFl:
                    comm.ERR(f"Cannot accept multiple files")
                    return comm.ERR_INCOPTUSAGE
                if pos + 1 not in args:
                    comm.ERR(f"Missing argument for -{opt}: file")
                    return comm.ERR_INCOPTUSAGE
                txtOrFl = args[pos + 1]
                isFl    = True

    if not bytes_ and not words and not lines:
        bytes_ = True
        words  = True
        lines  = True

    if not args or len(args) != 1:
        comm.ERR("Incorrect format")
        return comm.ERR_INCFORMAT

    if 'f' not in optVals and "-file" not in optVals:
        txtOrFl = args[sorted(args)[0]]

    if isFl:
        if not os.path.isfile(txtOrFl):
            comm.ERR(f"No such file: \"{txtOrFl}\"")
            return comm.ERR_NOFL
        try:
            with open(txtOrFl, buffering=1) as f:
                data = f.read()
        except PermissionError:
            comm.ERR(f"Access is denied: \"{txtOrFl}\"")
            return comm.ERR_PERMDENIED
        except UnicodeDecodeError:
            comm.ERR(f"Cannot decode file: \"{txtOrFl}\"")
            return comm.ERR_CANTDECODE

    else:
        data = txtOrFl

    toPrint = HELPER_WC(data, bytes_, words, lines)
    print("; ".join(toPrint))
    return comm.ERR_SUCCESS
