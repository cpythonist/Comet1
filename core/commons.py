#
# Comet 1 source code
# Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename   : src\\core\\commons.py
# Description: Contains methods and classes to be used in all parts of the
#              program (common code)
#

import os
import sys
import ctypes    as ct
import msvcrt    as ms
import logging   as lg
import shutil    as sh
import traceback as tb
import typing    as ty


class CustomLogger(lg.getLoggerClass()):
    """
    Custom logger extending the logging.Logger class to add separate
    functionality to the FATAL log level.
    """
    def __init__(self, name: str, level: int | str = lg.NOTSET) -> None:
        super().__init__(name, level)
        lg.addLevelName(FATAL, "FATAL")

    def info(self, msg: str, sl: int = 3, *args: ty.Any, **kwargs: ty.Any) -> None:
        if self.isEnabledFor(lg.INFO):
            self._log(lg.INFO, msg, args, **kwargs, stacklevel=sl)

    def debug(self, msg: str, sl: int = 3, *args: ty.Any, **kwargs: ty.Any) -> None:
        if self.isEnabledFor(lg.DEBUG):
            self._log(lg.DEBUG, msg, args, **kwargs, stacklevel=sl)

    def warning(self, msg: str, sl: int = 3, *args: ty.Any, **kwargs: ty.Any) -> None:
        if self.isEnabledFor(lg.WARNING):
            self._log(lg.WARNING, msg, args, **kwargs, stacklevel=sl)

    def error(self, msg: str, sl: int = 3, *args: ty.Any, **kwargs: ty.Any) -> None:
        if self.isEnabledFor(lg.ERROR):
            self._log(lg.ERROR, msg, args, **kwargs, stacklevel=sl)

    def critical(self, msg: str, sl: int = 3, *args: ty.Any, **kwargs: ty.Any) -> None:
        if self.isEnabledFor(lg.CRITICAL):
            self._log(lg.CRITICAL, msg, args, **kwargs, stacklevel=sl)

    def fatal(self, msg: str, sl: int = 3, *args: ty.Any, **kwargs: ty.Any) -> None:
        if self.isEnabledFor(FATAL):
            self._log(FATAL, msg, args, **kwargs, stacklevel=sl)


class CustomLogFormatter(lg.Formatter):
    """
    To apply custom formatting to the log message (like whitespace stripping).
    """
    def __init__(self, fmt: str | None = None, datefmt: str | None = None,
                 style: ty.Literal['%'] | ty.Literal['{'] | ty.Literal['$'] = '%',
                 validate: bool = True, *,
                 defaults: ty.Mapping[str, ty.Any] | None = None) -> None:
        self.lvlSyms = {
            lg.DEBUG: "D",
            lg.INFO: "I",
            lg.WARNING: "W",
            lg.ERROR: "E",
            lg.CRITICAL: "C",
            FATAL: "F"
        }
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record: lg.LogRecord) -> str:
        record.msg        = record.getMessage().strip()
        record.funcName   = record.funcName.lower()
        record.levelname2 = self.lvlSyms[record.levelno]
        return super().format(record)


def INITLOGGER() -> tuple[lg.Logger, lg.Logger, lg.Logger, lg.Logger,
                          lg.Logger, lg.Logger]:
    """
    Initialise logging components and logger.
    > return: Logger object after applying formatting rules and adding handlers
    NOTE: Please note that the Logger class is changed in this function with
          the function logging.setLogger
    """
    lg.captureWarnings(True)
    lg.setLoggerClass(CustomLogger)

    # > cnCometLgr handles logging to console from the interpreter itself,
    #   above WARN. Will be used by ERR(), CRIT() and FATAL();
    # > cnLgr handles logging to console from commands, above WARN. Will be
    #   used by ERR(), CRIT() and FATAL();
    # > cnCometDebugLgr handles logging to console, from the interpreter
    #   itself, of DEBUG, INFO, and anything above this. Will be used by
    #   DEBUG() and INFO();
    # > cnDebugLgr handles logging to console, from commands, of DEBUG,
    #   INFO, and anything above this. Will be used by DEBUG() and INFO();
    # > flLgr handles logging to a log file (log.log) of CRIT and above. Will
    #   be used by CRIT() and FATAL();
    lgr             = lg.getLogger(__name__)
    cnCometLgr      = lgr.getChild("COMET")
    cnLgr           = lgr.getChild("STDERR")
    cnDebugLgr      = lgr.getChild("OTHER")
    cnCometDebugLgr = lgr.getChild("MAINOTHER")
    flLgr           = lgr.getChild("FILE")
    lgr.setLevel(lg.DEBUG)

    cnCometFormatter      = CustomLogFormatter(
        fmt=(f"{ANSIBOLD + ANSIRED}%(levelname2)s:{ANSIRESET} "
             "comet: %(message)s")
    )
    cnFormatter           = CustomLogFormatter(
        fmt=(f"{ANSIBOLD + ANSIRED}%(levelname2)s:{ANSIRESET} "
             "%(funcName)s: %(message)s")
    )
    cnDebugFormatter      = CustomLogFormatter(
        fmt=(f"{ANSIBOLD}%(levelname2)s:{ANSIRESET} "
             "%(funcName)s: %(message)s")
    )
    cnCometDebugFormatter = CustomLogFormatter(
        fmt=(f"{ANSIBOLD}%(levelname2)s:{ANSIRESET} "
             "comet: %(message)s")
    )
    flFormatter           = CustomLogFormatter(
        fmt=("[%(asctime)s.%(msecs)03d]\n%(levelname)s:%(module)s:"
            "%(funcName)s:\n%(message)s\n--------"),
        datefmt="%z/%d-%m-%Y/%H:%M:%S"
    )

    cnHdlerComet      = lg.StreamHandler()
    cnHdler           = lg.StreamHandler()
    cnHdlerDebug      = lg.StreamHandler()
    cnCometHdlerDebug = lg.StreamHandler()
    flHdler           = lg.FileHandler(PTHJN(ORIGPTH, "log.log"), 'a',
                                       encoding="utf-8")

    cnHdlerComet.setFormatter(cnCometFormatter)
    cnHdler.setFormatter(cnFormatter)
    cnHdlerDebug.setFormatter(cnDebugFormatter)
    cnCometHdlerDebug.setFormatter(cnCometDebugFormatter)
    flHdler.setFormatter(flFormatter)

    cnHdlerComet.setLevel(lg.WARN)
    cnHdler.setLevel(lg.WARN)
    cnHdlerDebug.setLevel(lg.DEBUG)
    cnCometHdlerDebug.setLevel(lg.DEBUG)
    flHdler.setLevel(lg.CRITICAL)

    cnCometLgr.addHandler(cnHdlerComet)
    cnLgr.addHandler(cnHdler)
    flLgr.addHandler(flHdler)
    cnDebugLgr.addHandler(cnHdlerDebug)
    cnCometDebugLgr.addHandler(cnCometHdlerDebug)

    return lgr, cnCometLgr, cnLgr, cnDebugLgr, cnCometDebugLgr, flLgr


def ANSIOK() -> bool:
    """
    Checks if the terminal supports ANSI sequences.
    Thanks to Stack Overflow!
    > return: True if the terminal supports ANSI sequences, False otherwise.
    """
    kernel32 = ct.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    while ms.kbhit():
        ms.getch()
    sys.stdout.write("\x1b[6n\b\b\b\b")
    sys.stdout.flush()
    sys.stdin.flush()
    if ms.kbhit():
        if ord(ms.getch()) == 27 and ms.kbhit():
            if ms.getch() == b"[":
                while ms.kbhit():
                    ms.getch()
                return sys.stdout.isatty()
    return False


def CONSHELPSTR(srcList: list[str] | tuple[str, ...]) -> str:
    """
    Construct a help string.
    > param srcList: List of source strings for construction of the help string
    """
    return '\n'.join([line.expandtabs(4) for line in srcList])


def OPTSJOIN(opts: list[str] | tuple[str, ...] | set[str] | ty.KeysView[str]
             | ty.ValuesView[str] | dict[int, str]) -> str:
    """
    String formatting for printing options, like when an invalid option or
    too many options are provided.
    > param opts: The options to be present in the constrcuted string
    > return: The constructed "options" string
    """
    if isinstance(opts, dict):
        return ', '.join(f"'{i}'" for i in opts.values())
    return ', '.join(f"'{i}'" for i in opts)


def DEBUG(msg: str | Exception, sl: int = 3, raiser: str = "notComet") -> int:
    """
    Prints information to STDOUT. Was actually planned to be expanded.
    > param text: Text to be printed
    > return: None
    """
    if raiser == "notComet":
        CNDEBUGLGR.debug(repr(str(msg))[1:-1], sl=sl)
    elif raiser == "comet":
        CNCOMETDEBUGLGR.debug(repr(str(msg))[1:-1], sl=sl)
    return 0


def INFO(msg: str | Exception, sl: int = 3, raiser: str = "notComet") -> int:
    """
    Prints information to STDOUT. Was actually planned to be expanded.
    > param text: Text to be printed
    > return: None
    """
    if raiser == "notComet":
        CNDEBUGLGR.info(repr(str(msg))[1:-1], sl=sl)
    elif raiser == "comet":
        CNCOMETDEBUGLGR.info(repr(str(msg))[1:-1], sl=sl)
    return 0


def WARN(msg: str | Exception, sl: int = 3, raiser: str = "notComet") -> int:
    if raiser == "notComet":
        CNDEBUGLGR.warning(repr(str(msg))[1:-1], sl=sl)
    elif raiser == "comet":
        CNCOMETDEBUGLGR.warning(repr(str(msg))[1:-1], sl=sl)
    return 0


def ERR(msg: str | Exception, sl: int = 3, raiser: str = "notComet") -> int:
    toPrn = ''
    if raiser == "notComet":
        CNLGR.error(repr(str(msg))[1:-1], sl=sl)
    elif raiser == "comet":
        CNCOMETLGR.error(repr(str(msg))[1:-1], sl=sl)
    return 1


def CRIT(msg: str | Exception, logTxt: str, sl: int = 3,
         raiser: str = "notComet") -> int:
    if raiser == "notComet":
        CNLGR.critical(repr(str(msg))[1:-1], sl=sl)
    elif raiser == "comet":
        CNCOMETLGR.critical(repr(str(msg))[1:-1], sl=sl)
    FLLGR.critical(logTxt, sl=sl)
    return 2


def UNERR(msg: str | Exception, logTxt: str, sl: int = 3,
          raiser: str = "notComet") -> int:
    """
    Prints unknown errors to screen and/or logs said unknown errors.
    > param text: Text to be printed
    > param logStr: Text to be logged. If None, parameter "text" is used for
                    logging
    > param log: Determine if the error is to be logged
    > param func: Function name for error reporting
    > return: Error code (-1)
    """
    if raiser == "notComet":
        CNLGR.fatal(repr(str(msg))[1:-1], sl=sl)
    elif raiser == "comet":
        CNCOMETLGR.fatal(repr(str(msg))[1:-1], sl=sl)
    FLLGR.fatal(logTxt, sl=sl)
    return -1


def GETATTRFRMSETTFL(line: str, lineNo: int) -> tuple[str | int, str | int]:
    """
    Get the attribute name and value from a given line from the settings file.
    > param line: A string from the settings file
    > param lineNo: For error reporting; The line number of the given line
                    (index) in the settings file
    > return: A tuple that contains two strings, the first item being the
              attribute name and the second item being the attribute value,
              if the line is a proper formatted settings line. Else returns a
              tuple containing two integer zeroes.
    """
    attr, val = 0, 0
    for i, char in enumerate(line):
        if char == '=':
            attr = line[:i]
            val  = line[i+1:]
            break
    return attr, val


def _PROCDATA_RDSETT(line: str, i: int) \
        -> tuple[tuple[str, str] | None, int]:
    """
    Sub-function of function readSettings(...). Processes the line given from
    the settings file to obtain the attribute name and value.
    > param line: One line from the settings file
    > param i: The (zero-indexed) line number of the given line in the settings
               file
    > return: A tuple of length two. The first item is either a tuple of two
              strings, which represent the attribute name and the attribute
              value, if the line is valid. Else None. The second item is the
              error code
              0: Success
              # TODO: CHK THESE TWO!
              1: Invalid data
              2: Invalid line
    """
    try:
        # 1/0
        line = line.strip('\n')
        # Empty or whitespace line
        if not line:
            return None, 0
        attr, val = GETATTRFRMSETTFL(line, i+1)
        # Check for invalid data in the settings file
        if not (attr != 0 and val != 0) or isinstance(attr, int) \
                or isinstance(val, int):
            return None, 2
        # Path has a special symbol: '*' refers to the user directory.
        if attr == "path":
            usrDirRepr = repr(USRDIR)[1:-1]
            val = val.replace('*', usrDirRepr) if val else usrDirRepr
        return (attr, bytes(val, "utf-8").decode("unicode-escape")), 0

    except (SyntaxError, UnicodeDecodeError):
        ERR(f"Invalid data in settings file on line {i+1}")
        return None, 1


def RDSETT() -> dict[str, ty.Any] | None:
    """
    Read Clash settings from file src\\_settings.txt.
    > return: Settings dictionary or None if invalid or other errors.
    """
    settings: dict[str, ty.Any] = {}
    try:
        with open(SETTFL, 'r') as f:
            for i, line in enumerate(f):
                tmp = _PROCDATA_RDSETT(line, i)
                if tmp[0] != None and tmp[1] == 0:
                    settings[tmp[0][0].lower()] = tmp[0][1]
    except FileNotFoundError:
        try:
            open(SETTFL, 'w').close()
        except PermissionError:
            ERR("Access is denied: Unable to create settings file")
    return settings


def DICTSRCH(fndKey: ty.Any, givenDict: dict[ty.Any, ty.Any],
             caseIn: bool=False, returnMode: str = "vals") \
                -> list[ty.Any] | None:
    """
    Searches for a key in a dictionary and returns the value if the key was
    found, else returns None.
    Can perform case-insensitive search if the given key and any of the keys
    in the given dictionary is of type 'str'.
    Please note that the given dictionary must not contain any Nonetype
    values in it, as it may lead to confusion about the existance of the key.
    > param fndKey: The key to be searched in the dictionary
    > param givenDict: Given dictionary to be searched
    > param caseIn: Boolean to determine if case-insensitive search is to be
                    performed
    > return: Returns the value of the key, if the key is found in the
              dictionary, else returns None
    """
    keys: list[ty.Any]
    vals: list[ty.Any]
    keys = []
    vals = []
    fndKey = fndKey.lower() if isinstance(fndKey, str) and caseIn else fndKey
    for key in givenDict:
        if (key.lower() if caseIn and isinstance(key, str) else key) == fndKey:
            keys.append(key)
            vals.append(givenDict[key])
    if returnMode == "keys" and keys != []:
        return keys
    elif returnMode == "vals" and vals != []:
        return vals
    return None

def CASEINSENSMODSRCHANDRM(find: str, given: dict[str, ty.Any],
                           caseIn: bool=True) -> dict[str, ty.Any]:
    """
    Case-insensitive search and remove for a dictionary. Used for removing
    imported modules, if any is present in sys.modules (to be freshly
    imported). Case-insensitive is implemented because Windows file system
    is case-insensitive.
    > param find: Module name
    > param given: Dictionary of modules
    > param caseIn: To determine if case-insensitive search is to be performed
    > return: Updated dictionary
    """
    for key in list(given):
        if (find.lower() if caseIn else find) \
                == (key.lower() if caseIn else key):
            given.pop(key)
    return given


def LOWERLT(arr: list[str] | tuple[str, ...] | ty.KeysView[str]
            | ty.ValuesView[str] | dict[ty.Any, str]) -> list[str]:
    """
    Converts all items of a list, tuple, dict_values() object or values of a
    dictionary containing strings to lowercase.
    > param arr: List, tuple, dict_values() object or dictionary whose
                 elements are to be converted to lowercase
    > return: Converted list
    """
    if isinstance(arr, dict):
        return [i.lower() for i in arr.values()]
    return [i.lower() for i in arr]


def PARAMOK(param: str) -> int:
    """
    Check a parameter if it satisfies the necessary conditions to be a
    parameter name.
    > param param: Name to be checked
    > return: True if the parameter is OK else False
    """
    if not param:
        return False
    return not bool([i for i in param
                     if ord(i) not in CAPITALLETT
                     and ord(i) not in SMALLLETT])


def SETSETT(param: str, value: str) -> int:
    """
    Sets an attribute's value in the settings file.
    > param dirname: Clash root directory
    > param param: Attribute to be set
    > param value: Value to be set to attribute
    > param howMany: Number of values to be set
    > return: Error code
        0: Success
        1: Attribute not found
        2: Invalid parameter name
    """
    reqLine = param + '=' + value + '\n'

    if not PARAMOK(param):
        return 2

    try:
        sh.copyfile(SETTFL, SETTTMP)

        with open(SETTFL, 'w') as f, open(SETTTMP, 'r') as g:
            for line in g:
                linePar = line.partition('=')
                if linePar[1] == '':
                    f.write(line)
                    continue
                if linePar[0].lower() == param.lower():
                    f.write(reqLine)
                else:
                    f.write(line)

        os.remove(SETTTMP)
        return 0

    except FileNotFoundError:
        try:
            with open(SETTFL, 'w') as f:
                f.write(reqLine)
            return 0
        except PermissionError:
            return 5

    except PermissionError:
        return 5


def RDPREVCHAR(fd: ty.TextIO) -> str | Exception:
    """
    Reads the previous character from a file.
    > param fd: File object
    > return: Previous character
    """
    if not fd.tell():
        return ''
    fd.seek(fd.tell() - 1, 0)
    return fd.read(1)


def DICTUPDATE(dict1: dict[ty.Any, ty.Any], dict2: dict[ty.Any, ty.Any]) \
        -> dict[ty.Any, ty.Any]:
    """
    Function declared to make the type checker shut up, which was bitching that
    dict.update() method's return was partially unknown, that type Overload
    cannot be assigned to type dict.
    > param dict1: First dictionary
    > param dict2: Second dictionary
    > return: Updated dictionary
    """
    for key in dict2:
        dict1[key] = dict2[key]
    return dict1


COMETHELP       = ("The Comet interpreter, version 1.0", '', "OPTIONS",
                   "-d / --debug", "\tEnable debugging mode", "-h / --help",
                   "\tDisplay this help message")
PTHJN           = os.path.join
GETEXC          = tb.format_exc
USRDIR          = os.path.expanduser('~')
ORIGPTH         = os.path.dirname(os.path.dirname(__file__))
ANSI            = ANSIOK()
ANSIBOLD        = "\033[1m"      if ANSI else ''
ANSIBLINK       = "\033[5m"      if ANSI else ''
ANSIBLUE        = "\033[94m"     if ANSI else ''
ANSICLS         = "\033[H\033[J" if ANSI else ''
ANSICYAN        = "\033[96m"     if ANSI else ''
ANSIGREEN       = "\033[92m"     if ANSI else ''
ANSIHEADER      = "\033[95m"     if ANSI else ''
ANSIRED         = "\033[91m"     if ANSI else ''
ANSIRESET       = "\033[0m"      if ANSI else ''
ANSIUNDERLINE   = "\033[4m"      if ANSI else ''
ANSIYELLOW      = "\033[93m"     if ANSI else ''
CAPITALLETT     = range(65, 91)
SMALLLETT       = range(97, 123)
FATAL           = 60
ALLLGRS         = INITLOGGER()
LGR             = ALLLGRS[0]
CNCOMETLGR      = ALLLGRS[1]
CNLGR           = ALLLGRS[2]
CNDEBUGLGR      = ALLLGRS[3]
CNCOMETDEBUGLGR = ALLLGRS[4]
FLLGR           = ALLLGRS[5]
STDOUT          = ''
STDERR          = ''
SETTFL          = PTHJN(ORIGPTH, "_settings.txt")
SETTTMP         = PTHJN(ORIGPTH, "bin", "_settings.tmp")
LOGDIR          = PTHJN(ORIGPTH, "logs")
LOGCOMMFL       = PTHJN(LOGDIR, "commonsErr.log")
DFLTSETT        = {
    "prompt"     : "%7[%E]%9 (%4%U%9@%C) %1%5%P%9 $ ",
    "path"       : USRDIR,
    "pathSett"   : '',
    "cdtodirs"   : "yes",
    "execscripts": "yes",
    "title"      : '',
    "intro"      : "on"
}
