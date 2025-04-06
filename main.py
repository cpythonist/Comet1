#
# Comet 1 source code
# Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename: src\\main.py
# Description: The main program
#

import os
import sys
import datetime           as dt
import getpass            as gp
import platform           as pf
import prompt_toolkit     as pt
import typing             as ty
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings

# Add directory "src\\core" to list variable sys.path
sys.path.insert(1, os.path.dirname(__file__) + os.sep + "core")
import comet
import commons  as comm
sys.path.pop(1)


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


class _Completer:
    def __init__(self, interpreter: comet.Interpreter, prompt: str,
                 pth: str) -> None:
        self.interpreter    = interpreter
        self.prompt         = prompt
        self.pth            = pth

    def getCommands(self) -> list[str]:
        return [func for func in dir(self.interpreter) if func.isupper()]

    def complete(self, txt: str, state: int) -> str | None:
        self.opts = os.listdir('.')

        if state == 0:
            if not txt:
                self.matches = self.opts[:]
            else:
                self.matches = [s for s in self.opts
                                if s and s.startswith(txt)]

        try:
            return self.matches[state]
        except IndexError:
            return None

    def ctrlLClrScr(self) -> None:
        os.system("cls")
        print("\033[0;0H")
        print(promptUpdater(self.interpreter, self.prompt),
              end='', flush=True)

    def display_matches(self, substitution, matches, longest_match_length):
        line_buffer = rl.get_line_buffer()
        columns = os.get_terminal_size().columns

        print()

        tpl = "{:<" + str(int(max(map(len, matches)) * 1.2)) + "}"

        buffer = ""
        for match in matches:
            match = tpl.format(match[len(substitution):])
            if len(buffer + match) > columns:
                print(buffer)
                buffer = ""
            buffer += match

        if buffer:
            print(buffer)

        print("> ", end="")
        print(line_buffer, end="")
        sys.stdout.flush()


class CometCompleter(Completer):
    def __init__(self, interpreter: comet.Interpreter) -> None:
        self.interpreter = interpreter

    def get_completions(self, document, complete_event) \
            -> ty.Generator[Completion, None, None]:
        for item in os.scandir(self.interpreter.path):
            yield Completion(item.name, start_position=0)


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
        parser      = comet.Parser()
        interpreter = comet.Interpreter(
            parser,
            comm.DFLTSETT if (tmp := comm.RDSETT()) is None else tmp,
            __file__.removesuffix(".py") + ".exe"
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
