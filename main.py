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
import datetime       as dt
import getpass        as gp
import platform       as pf
import prompt_toolkit as pt

# Add src\\core to sys.path
sys.path.insert(1, os.path.dirname(__file__) + os.sep + "core")
import comet
import commons  as comm
sys.path.pop(1)


def parseArgs() -> dict[str, bool | str]:
    toReturn: dict[str, bool | str]
    validArgs    = ("-d", "--debug", "-h", "--help")
    toReturn     = {"debug": False}
    errEncntered = False

    for arg in sys.argv[1:]:
        lowerArg = arg.lower()
        if lowerArg not in validArgs:
            comm.ERR(f"Invalid argument to Comet: \'{arg}\'", raiser="comet")
            errEncntered = True
            continue
        if lowerArg == "-d" or lowerArg == "--debug":
            toReturn["debug"] = True
        elif lowerArg == "-h" or lowerArg == "--help":
            print(comm.CONSHELPSTR(comm.COMETHELP))
            sys.exit(0)

    if errEncntered:
        comm.ERR("Please use the -h or --help option for more information.",
                 raiser="comet")
        sys.exit(1)

    return toReturn


def promptUpdater(interpreter: comet.Interpreter, prompt: str) -> str:
    """
    Updates the Clash dynamic prompt.
    > param prompt: The raw prompt string
    > param path: Operating path of the interpreter/shell
    > param lastErr: For last command error in the prompt
    > return: The updated prompt string
    """
    # Var i keeps track of idx to be accessed in var prompt during next
    # iteration. For loop was not used as var i could not be changed flexibly
    # in a for loop.
    i            = 0
    length       = len(prompt)
    returnPrompt = ''
    while i < length - 1:
        # Var toAdd is/are character(s) to add to str to be returned, i.e. var
        # returnPrompt. Var skip is responsible for skipping chars which were
        # replaced.
        toAdd = prompt[i]
        skip  = 1

        if prompt[i] == '%' and prompt[i+1].lower() in "cdenopstuvw0123456789%":
            if prompt[i+1] in "cC":
                toAdd = os.environ["COMPUTERNAME"]
            elif prompt[i+1] in "dD":
                toAdd = dt.date.today().strftime("%d/%m/%Y")
            elif prompt[i+1] in "eE":
                toAdd = ('x' if interpreter.err else '.')
            elif prompt[i+1] in "nN":
                toAdd = '\n'
            elif prompt[i+1] in "oO":
                toAdd = pf.system()
            elif prompt[i+1] in "pP":
                toAdd = interpreter.path
            elif prompt[i+1] in "sS":
                toAdd = ' '
            elif prompt[i+1] in "tT":
                toAdd = dt.datetime.now().strftime("%H:%M:%S.%f")
            elif prompt[i+1] in "uU":
                toAdd = gp.getuser()
            elif prompt[i+1] in "vV":
                toAdd = "11" if \
                    (pf.release() == "10" and \
                     int(pf.version().split('.')[2]) > 22000) \
                        else pf.release()
            elif prompt[i+1] in "wW":
                toAdd = os.getcwd()[0]
            elif prompt[i+1] == '0':
                toAdd = comm.ANSIBLINK
            elif prompt[i+1] == '1':
                toAdd = comm.ANSIBOLD
            elif prompt[i+1] == '2':
                toAdd = comm.ANSIUNDERLINE
            elif prompt[i+1] == '3':
                toAdd = comm.ANSIBLUE
            elif prompt[i+1] == '4':
                toAdd = comm.ANSICYAN
            elif prompt[i+1] == '5':
                toAdd = comm.ANSIGREEN
            elif prompt[i+1] == '6':
                toAdd = comm.ANSIRED
            elif prompt[i+1] == '7':
                toAdd = comm.ANSIYELLOW
            elif prompt[i+1] == '8':
                toAdd = comm.ANSIHEADER
            elif prompt[i+1] == '9':
                toAdd = comm.ANSIRESET
            elif prompt[i+1] == '%':
                toAdd = '%'
            skip = 2

        returnPrompt += toAdd
        i            += skip
    # Edge case (literally too): One char is left at end, i.e. two chars were
    # to be substituted and one char was left at end.
    if i == length-1:
        returnPrompt += prompt[i]
    return returnPrompt.replace(os.path.expanduser('~'), '~')


def main() -> None:
    """
    All error codes:
    -1: Unknown error
    0: Success
    1: Error
    2: Unknown command
    3: Command too long
    4: Command interrupted
    5: Failed to import module
    6: Is a directory
    7: Is not a Comet script file
    The function to set up the interpreter object, and also handle
    KeyboardInterrupts and EOFErrors. Handles fatal errors, and logs them to
    a file before exiting.
    """
    try:
        if not comm.ANSIOK():
            print("Terminal does not support ANSI; You may see some garbled "
                  "text during interpreter startup")
        
        mainArgs    = parseArgs()
        parser      = comet.Parser()
        interpreter = comet.Interpreter(
            parser,
            comm.DFLTSETT if (tmp := comm.RDSETT()) is None else tmp,
            __file__.removesuffix(".py") + ".exe",
            mainArgs["debug"]
        )

        prompt = interpreter.settings.get("prompt")
        pth    = interpreter.settings.get("path")
        if prompt is None:
            prompt = comm.DFLTSETT["prompt"]
        if pth is None:
            pth = comm.DFLTSETT["path"]

        session = pt.PromptSession()

    except Exception as e:
        comm.ERR("Fatal error encountered; could not initialise the "
                 "interpreter; see the log for details", raiser="comet")
        comm.UNERR(e, comm.GETEXC())
        sys.exit(-1)

    while True:
        try:
            # Separate print statement for displaying prompt as pyreadline3
            # removes ANSI codes from prompt when used with input()
            inpLn = session.prompt(pt.ANSI(promptUpdater(interpreter, prompt)))
            interpreter.execute(inpLn)

        except KeyboardInterrupt:
            # TODO: Assign separate error code to this, or whatever! Change it!
            interpreter.err               = 4
            interpreter.varTable["error"] = '4'
            print(f"{comm.ANSIBLUE}^C{comm.ANSIRESET}")

        except EOFError:
            print("Bye")
            sys.exit(0)

        except Exception as e:
            comm.UNERR(e, comm.GETEXC())
            sys.exit(-1)


if __name__ == "__main__":
    main()
