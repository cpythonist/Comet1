import os
import sys
import shutil as sh
import typing as ty

srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Displays the disc information.", "USAGE: disc [-h]",
    "OPTION(S)", "\t-h / --help", "\t\tHelp message"
)


def DISC(interpreter: comet.Interpreter, command: str, args: dict[int, str],
         opts: dict[int, str], fullComm: str, stream: ty.TextIO,
         op: str) -> int:
    """
    Displays the disc information.
    > param interpreter: Interpreter object
    > param command: Command name
    > param args: Dictionary of arguments
    > param opts: Dictionary of options
    > param fullComm: Full input line
    > param stream: Original STDOUT
    > param op: Operation next in line to be performed
    > return: Error code (0-2) (ref. src\\errCodes.txt)
    """
    optVals = comm.lowerLT(opts.values())
    validOpts = {'h', "-help"}

    if opts:
        if tmp := (set(optVals) - validOpts):
            comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
            return 2
        if 'h' in optVals or "-help" in optVals:
            print(comm.CONSHELPSTR(helpStr))
            return 0

    if args:
        comm.ERR("Incorrect format")
        return 1

    drives = [f"{chr(i)}:\\" for i in range(65, 91)
              if os.path.exists(f"{chr(i)}:\\")]
    for drive in drives:
        total, used, free = [round(i / 10 ** 9, 2)
                             for i in sh.disk_usage(drive)]
        print(f"{drive}  {total}GB  {used}GB  {free}GB")

    return 0
