#
# Comet 1 source code
# Copyright (c) 2025 Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename: src\\main.py
# Description: The main program
#

import os
import sys
import pathlib        as pl
import platform       as pf
import prompt_toolkit as pt

# Add src\\core to sys.path
sys.path.insert(1, os.path.dirname(__file__) + os.sep + "core")
import comet
import commons as comm
import parser  as par
sys.path.pop(1)


def parseArgs() -> dict[str, bool | str]:
    toReturn: dict[str, bool | str]
    validArgs     = ("-d", "-wd", "-h",
                     "--debug", "--workingdirectory", "--help")
    toReturn      = {"debug": False}
    errEncntered  = False
    reqSysArgv    = sys.argv[1:]
    lenReqSysArgv = len(reqSysArgv)
    skip          = 0

    for i, arg in enumerate(reqSysArgv):
        # Skip ones that were values for the previous arguments
        if skip != 0:
            skip -= 1
            continue

        lowerArg = arg.lower()
        if lowerArg not in validArgs:
            comm.ERR(f"Invalid argument/option to Comet: \'{arg}\'",
                     raiser='c')
            errEncntered = True
            continue

        if lowerArg == "-d" or lowerArg == "--debug":
            toReturn["debug"] = True

        elif lowerArg == "-wd" or lowerArg == "--workingdirectory":
            if i >= lenReqSysArgv - 1:
                comm.ERR(f"Expected value for option '{arg}'", raiser='c')
                errEncntered = True
                continue

            toReturn["workingdirectory"] = reqSysArgv[i + 1]
            skip                         = 1

        elif lowerArg == "-h" or lowerArg == "--help":
            print(comm.DECOMPSTR(comm.COMETHELP))
            sys.exit(0)

    if errEncntered:
        comm.INFO("Use the -h or --help option for more information.",
                  raiser='c')
        sys.exit(1)

    return toReturn


def prmptUpdtr(intpr: comet.Intrp, prompt: str) -> str:
    """
    Updates the Clash dynamic prompt.
    > param intr: The interpreter object
    > param prompt: The raw prompt string
    > return: The updated prompt string
    """
    i      = 0
    len_   = len(prompt)
    retStr = ''

    while i < len_ - 1:
        toAdd  = prompt[i]
        nxtChr = prompt[i + 1].lower()
        skip   = 1

        if toAdd == '%' and nxtChr in "cdenopstuvw0123456789%":
            if comm.PROMPTCODES.get(nxtChr) is not None:
                toAdd = comm.PROMPTCODES[nxtChr]
                if callable(toAdd):
                    try:
                        toAdd = toAdd()
                    except Exception as e:
                        comm.WARN(f"Prompt code %{nxtChr} or %{nxtChr.upper()} failed",
                                  raiser='c')
                        toAdd = "[FAIL]"

            elif nxtChr == 'e':
                toAdd = ('x' if intpr.err else '.')

            elif nxtChr == 'n':
                toAdd = '\n'

            elif nxtChr == 'p':
                toAdd = intpr.path

            elif nxtChr == 's':
                toAdd = ' '

            elif nxtChr in "vV":
                toAdd = comm.PROMPTCODES[nxtChr]
                ver   = pf.version().split('.')[2]
                try:
                    ver = int(ver)
                    if toAdd == "10" and ver > 22000:
                        toAdd = "11"
                except ValueError:
                    comm.WARN("What the hell is that version?!")

            elif nxtChr == '%':
                toAdd = '%'

            skip = 2

        retStr += toAdd
        i      += skip

    # Edge case (literally too): One char is left at end, i.e. two chars were
    # to be substituted and one char was left at end.
    if i == len_ - 1:
        retStr += prompt[i]

    return retStr


def main() -> None:
    """
    Sets up the interpreter object, and also handles ^C interrupts and EOFs.
    Handles fatal errors, and logs them to a file before exiting.
    Refer to src\\errCodes.txt for the error codes returned by the interpreter.
    """
    # Reincarnation loop: Restart interpreter on SIGREINCARNATE
    while True:
        if not comm.ANSIOK():
            comm.WARN("Terminal does not support ANSI; You may see some garbled text during interpreter startup")

        mainArgs = {"debug": False, "workingdirectory": None}
        mainArgs.update(parseArgs())

        try:
            parser = par.Parser()
            intrp  = comet.Intrp(
                parser,
                comm.DFLTSETT if (tmp := comm.RDSETT()) is None else tmp,
                str(pl.Path(sys.argv[0]).resolve()),
                mainArgs
            )
            parser.setIntrp(intrp)

            prompt  = intrp.settings.get("prompt", comm.DFLTSETT["prompt"])
            session = pt.PromptSession()

        except Exception as e:
            comm.ERR("Fatal error; could not initialise the interpreter; see "
                     "the log for details", raiser='c')
            comm.UNERR(e, comm.GETEXC())
            sys.exit(-1)

        # This try statement exists for the sole reason of catching SIGREINCARNATE
        # and then reincarnating the interpreter
        try:
            while True:
                try:
                    inpLn = session.prompt(pt.ANSI(prmptUpdtr(intrp, prompt)))
                    code  = intrp.execute(inpLn)
                    intrp.setErrCode(code)

                except KeyboardInterrupt:
                    intrp.setErrCode(comm.ERR_INTERRUPT)
                    print(comm.ANSIBLUE + "^C" + comm.ANSIRESET)

                except comm.SIGREINCARNATE:
                    raise comm.SIGREINCARNATE()

        except EOFError:
            print(f"{comm.ANSIGREEN}Bye{comm.ANSIRESET}")
            sys.exit(0)

        except comm.SIGREINCARNATE:
            continue
        
        except KeyboardInterrupt:
            pass

        except Exception as e:
            comm.UNERR(e, comm.GETEXC())
            sys.exit(-1)


if __name__ == "__main__":
    main()
