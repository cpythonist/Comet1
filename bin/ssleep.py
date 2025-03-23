import os
import sys
import time
import typing as ty

srcDir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1, os.path.join(srcDir, "core"))
import comet
import commons as comm
sys.path.pop(1)

helpStr = (
    "Wait a certain amount of time before continuing.",
    "USAGE: sleep [-h] [-n] time ...", "ARGUMENT(S)", "\ttime",
    "\t\tTime(s) to wait in seconds", "OPTION(S)", "\t-h / --help",
    "\t\tHelp message", "\t-n / --notify",
    "\t\tNotify user before sleep"
)


def SLEEP(interpreter: comet.Interpreter, command: str, args: dict[int, str],
          opts: dict[int, str], fullComm: str, stream: ty.TextIO,
          op: str) -> int:
        """
        Wait a certain amount of time before continuing.
        > param interpreter: Interpreter object
        > param command: Command name
        > param args: Dictionary of arguments
        > param opts: Dictionary of options
        > param fullComm: Full input line
        > param stream: Original STDOUT
        > param op: Operation next in line to be performed
        > return: Error code (0-2, 104) (ref. src\\errCodes.txt)
        Error code 104:
            Invalid time value (expected float)
        """
        notify    = False
        err       = 0
        optVals   = comm.lowerLT(opts.values())
        validOpts = {'n', 'h', "-notify", "-help"}

        if opts:
            if tmp := (set(optVals) - validOpts):
                comm.ERR(f"Unknown option(s): {comm.OPTSJOIN(tmp)}")
                return 2
            if 'h' in optVals or "-help" in optVals:
                print(comm.CONSHELPSTR(self.helpSLEEP))
                return 0
            for opt in optVals:
                if opt == 'n' or opt == '-notify':
                    notify = True

        if not args:
            comm.ERR("Incorrect format")
            return 1

        times = []
        for arg in args.values():
            try:
                times.append(float(arg))
            except ValueError:
                comm.ERR(f"Invalid time value: '{arg}'")
                return 104

        for validArg in times:
            if notify:
                stream.write(f"Sleeping {validArg}s...\n")
                stream.flush()
            time.sleep(float(validArg))

        return err
