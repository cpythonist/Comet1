#
# Comet 1 source code
# Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename        : src\\main.py
# File description: The main program
#

import os
import sys
import datetime  as dt
import getpass   as gp
import platform  as pf

# Add directory "src\\core" to list variable sys.path
sys.path.insert(1, os.path.dirname(__file__) + os.sep + "core")
import comet
import commons  as comm
sys.path.pop(1)


def promptUpdater(interpreter: comet.Interpreter, prompt: str, path: str,
                  lastErr: int) -> str:
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

        if prompt[i] == '%' and prompt[i+1].lower() in "cdenopstuvw%":
            if prompt[i+1] in "cC":
                toAdd = os.environ["COMPUTERNAME"]
            elif prompt[i+1] in "dD":
                toAdd = dt.date.today().strftime("%d/%m/%Y")
            elif prompt[i+1] in "eE":
                toAdd = ('x' if lastErr else '.')
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
            elif prompt[i+1] == '%':
                toAdd = '%'
            skip = 2

        returnPrompt += toAdd
        i            += skip
    # Edge case (literally too): One char is left at end, i.e. two chars were
    # to be substituted and one char was left at end.
    if i == length-1:
        returnPrompt += prompt[i]
    return returnPrompt


def main():
    """
    All error codes:
    -1: Unknown error
    0 : Success
    1 : Error
    2 : Unknown command
    3 : Command too long
    4 : Command interrupted
    5 : Failed to import module
    6 : Is a directory
    7 : Is not a Comet script file
    The function to set up the interpreter object, and also handle
    KeyboardInterrupts and EOFErrors. Handles fatal errors, and logs them to
    a file before exiting.
    > param: None
    > return: None
    """
    try:
        if not comm.ANSIOK():
            ANSIChoice = input("This terminal does not support ANSI codes; "
                               "you may see garbled text on running this "
                               "application. Proceed: y/n? ").strip().lower()
            if ANSIChoice != 'y':
                if ANSIChoice != 'n':
                    print("Invalid; exiting...")
                sys.exit(0)
        parser      = comet.Parser()
        interpreter = comet.Interpreter(
            parser,
            comm.DEFLTSETT if (tmp := comm.RDSETT()) is None else tmp,
            __file__.removesuffix(".py") + ".exe"
        )
        defltPrompt = comm.DEFLTSETT["prompt"]
        defltPth    = comm.DEFLTSETT["path"]
        os.system('')
    except Exception as e:
        comm.UNERR(e, comm.GETEXC())
        sys.exit(-1)

    while True:
        try:
            print(
                promptUpdater(
                    interpreter,
                    tmp if (tmp := interpreter.settings.get("prompt")) is not None \
                        else defltPrompt,
                    tmp if (tmp := interpreter.settings.get("path")) is not None \
                        else defltPth,
                    interpreter.err
                ),
                end=''
            )
            promptInp = input()
            interpreter.execute(promptInp)

        except KeyboardInterrupt:
            interpreter.err               = 4
            interpreter.varTable["error"] = '4'
            print("^C")

        except EOFError:
            print("Bye")
            sys.exit(0)

        except Exception as e:
            comm.UNERR(e, comm.GETEXC())
            sys.exit(-1)


if __name__ == "__main__":
    main()
