#
# Infinite Inc.
# Written by Thiruvalluvan Kamaraj
# Licenced under the Apache-2.0 Licence
#
# Filename: src\\pc.py
# Description: Build system for Comet 1
#

import os
import sys
import pathlib    as pl
import platform   as pf
import shutil     as sh
import subprocess as sp
import traceback  as tb

MAJORMINORVER = str(sys.version_info.major) + str(sys.version_info.minor)
ARCHI         = pf.machine().lower()

BOLD       = "\033[1m"
BLINK      = "\033[5m"
BLUE       = "\033[94m"
CYAN       = "\033[96m"
GREEN      = "\033[92m"
RED        = "\033[91m"
RESET      = "\033[0m"
UNDERLINE  = "\033[4m"
YELLOW     = "\033[93m"
BOLDRED    = BOLD + RED
BOLDCYAN   = BOLD + CYAN
BOLDGREEN  = BOLD + GREEN
BOLDYELLOW = BOLD + YELLOW

ERR_UNKNOWN       = -1
ERR_SUCCESS       = 0
ERR_CALLEDPROCERR = 1
ERR_PERMDENIED    = 2
ERR_INVFLTYPE     = 3
ERR_PARSEARGS     = 4
ERR_NOFL          = 5
ERR_RUNERR        = 6
ERR_FLNMSERR      = 7

HELPSTR = f"""{BOLDGREEN}USAGE:{RESET} python.exe .\\{os.path.basename(__file__)} options file

{BOLDGREEN}OPTIONS{RESET}
-na / --noasserts
    Disable assertions
-nrd / --normdocstrs
    Do not remove docstrings
-nro / --normout
    Do not remove Nuitka output (file.build)
-nq / --noquiet
    Do not suppress output
-w / --warn
    Do not suppress Python runtime warnings
-t / --trace
    Print stack trace on encountering errors
-ns / --nostandalone
    Do not build in "standalone" mode (Nuitka), i.e. build in "onefile" mode
-ncb / --nocompbin
    Do not compile bin files
-ncc / --nocompcore
    Do not compile core files
-ncm / --nocompmain
    Do not compile main file
-naf / --noaliasesfile
    Do not copy aliases file
-nsf / --nosettingsfile
    Do not copy settings file
-nef / --noerrorcodesfile
    Do not copy error codes file
-i / --icon
    Icon file (.ico) to use
-f / --file
    Files to build
-r / --run
    Run output exectutable
-j / --jobs
    Specify number of jobs
-h / --help
    Display help message
"""


def reportCalledProcessError(e: sp.CalledProcessError) -> None:
    """
    Reports a subprocess.CalledProcessError, i.e. when a command fails, to the user.
    > param e: Instance of class CalledProcessError
    """
    print(f"{BOLDRED}FAIL:{RESET} Build failed on command: {' '.join(e.cmd)}")
    print(f"{BOLD + CYAN}STDOUT:{RESET}{('\n' + e.stdout) if e.stdout else "[NULL]"}")
    print(f"{BOLDRED}STDERR:{RESET}{('\n' + e.stderr) if e.stderr else "[NULL]"}")


def reportPermErr(e: PermissionError, trace: bool) -> None:
    """
    Reports a PermissionError to the user.
    > param e: Instance of class PermissionError
    > param trace: Print stack trace
    """
    print(f"{BOLDRED}FATAL:{RESET} Permission error encountered")
    if trace:
        print("TRACEBACK:")
        tb.print_exc() if trace else None
    else:
        print(f"({e.__class__.__name__}) {e}")


def reportUnknErr(e: Exception, trace: bool) -> None:
    """
    Reports an unknown error to the user.
    > param e: Instance of class Exception
    > param trace: Print stack trace
    """
    print(f"{BOLDRED}FATAL:{RESET} Unknown error encountered")
    if trace:
        print(f"{BOLD}TRACEBACK:{RESET}")
        tb.print_exc() if trace else None
    else:
        print(f"({e.__class__.__name__}) {e}")


def reportInvFlType() -> None:
    """
    Reports an invalid file type to the user.
    """
    print(f"{BOLDRED}ERROR:{RESET} Invalid file type")


def parseArgs() -> tuple[dict[str, bool | str | list[str] | None], int]:
    """
    Parse the arguments passed to the build script.
    > return: Tuple of dictionary of arguments and integer error code
    """
    toRet: dict[str, bool | str | list[str] | None]
    args      = sys.argv[1:]
    lenArgs   = len(args)
    flGiven   = False
    iconGiven = False
    prnHelp   = False
    errEncd   = False
    skip      = 0
    toRet     = {
        "noasserts"       : True,
        "normdocstrs"     : False,
        "normout"         : False,
        "noquiet"         : False,
        "warn"            : False,
        "trace"           : False,
        "nostandalone"    : False,
        "run"             : False,
        "fl"              : None,
        "icon"            : None,
        "nocompbin"       : False,
        "nocompcore"      : False,
        "nocompmain"      : False,
        "noaliasesfile"   : False,
        "nosettingsfile"  : False,
        "noerrorcodesfile": False,
        "jobs"            : '',
        "flnms"           : []
    }

    for idx, arg in enumerate(args):
        if skip:
            skip -= 1
            continue

        argL = arg.lower()

        if argL in ("-na", "--noasserts"):
            toRet["noasserts"] = False

        elif argL in ("-nrd", "--normdocstrs"):
            toRet["normdocstrs"] = False

        elif argL in ("-nro", "--normout"):
            toRet["normout"] = False

        elif argL in ("-nq", "--noquiet"):
            toRet["noquiet"] = True

        elif argL in ("-w", "--warn"):
            toRet["warn"] = True

        elif argL in ("-t", "--trace"):
            toRet["trace"] = True

        elif argL in ("-ns", "--nostandalone"):
            toRet["nostandalone"] = False

        elif argL in ("-ncb", "--nocompbin"):
            toRet["nocompbin"] = True

        elif argL in ("-ncc", "--nocompcore"):
            toRet["nocompcore"] = True

        elif argL in ("-ncm", "--nocompmain"):
            toRet["nocompmain"] = True

        elif argL in ("-naf", "--noaliasesfile"):
            toRet["noaliasesfile"] = True

        elif argL in ("-nsf", "--nosettingsfile"):
            toRet["nosettingsfile"] = True

        elif argL in ("-nef", "--noerrorcodesfile"):
            toRet["noerrorcodesfile"] = True
        
        elif argL in ('-j', "--jobs"):
            if idx >= lenArgs - 1:
                print(f"Expected argument for {arg}; pos {idx + 1}")
                errEncd = True
                continue
            arg = args[idx + 1]
            try:
                int(arg)
            except ValueError:
                print(f"Expected integer for {arg}; pos {idx + 1}")
                errEncd = True
                continue
            finally:
                skip = 1
            toRet["jobs"] = arg

        elif argL in ("-i", "--icon"):
            if iconGiven:
                print(f"Cannot accept multiple icons: \"{arg}\"")
                errEncd = True
                continue
            if idx < lenArgs - 1:
                toRet["icon"] = args[idx + 1]
                skip          = 1
            else:
                print(f"Expected argument for {arg}; pos {idx + 1}")
                errEncd = True

        elif argL in ("-f", "--file"):
            if idx < lenArgs - 1:
                toRet["flnms"].append(args[idx + 1])
                skip = 1
            else:
                print(f"Expected argument for {arg}; pos {idx + 1}")
                errEncd = True

        elif argL in ("-r", "--run"):
            toRet["run"] = True

        elif argL in ("-h", "--help"):
            prnHelp = True

        else:
            if flGiven:
                print(f"Cannot accept multiple files: \"{arg}\"")
                errEncd = True
                continue
            toRet["fl"] = arg
            flGiven     = True

    if errEncd:
        print("Use -h or --help for the help message")
        return {}, ERR_PARSEARGS

    if prnHelp:
        print(HELPSTR)
        return {}, ERR_SUCCESS

    return toRet, ERR_SUCCESS


def compileBin(env: dict[str, str], srcBinDir: str, binDir: str, noasserts: bool,
               normdocstrs: bool, warn: bool, normout: bool, noquiet: bool,
               trace: bool, jobs: str, fls: list[str]) -> int:
    """
    Compiles command files (files present in src\\bin).
    > param env: Environment variables to use
    > param srcBinDir: Source directory for bin files
    > param binDir: Build directory for bin files
    > param noasserts: Do not allow assertions
    > param normdocstrs: Do not remove docstrings
    > param warn: Do not suppress Python runtime warnings
    > param normout: Do not remove output (prog.build directory)
    > param noquiet: Do not suppress output
    > param trace: Print stack trace
    > param fls: Files to compile (empty to compile all)
    > return: Integer error code
    """
    fls = [os.path.basename(pl.Path(i).resolve()).lower() for i in fls]
    print(f"{BOLDGREEN}Using Python at {sys.executable} for BIN FILES{RESET}")

    for item in os.scandir(srcBinDir):
        if not os.path.isfile(item):
            continue

        itemNm, itemExt = os.path.splitext(item.name)
        if not itemExt == ".py":
            continue

        if fls and item.name.lower() not in fls:
            continue

        command = [
            sys.executable,
            "-OO",
            "-W",
            "error",
            "-m",
            "nuitka",
            "--module",
            "--include-module=ctypes",
            # f"--include-plugin-directory={srcBinDir}",
            "--python-flag=no_docstrings" if not normdocstrs else '',
            "--python-flag=-O" if noasserts else '',
            "--python-flag=no_warnings" if not warn else '',
            f"--jobs={jobs}" if jobs else '',
            "--remove-output" if not normout else '',
            "--no-pyi-file",
            f"--output-dir={binDir}",
            "--quiet" if not noquiet else '',
            item.path
        ]
        command = [i for i in command if i]

        try:
            print(f"{BOLD}Execute:{RESET} {' '.join(command)}")
            sp.run(command, env=env, capture_output=True if not noquiet else False,
                   text=True, check=True)
            targFlNm = os.path.join(binDir, itemNm + ".pyd")
            origFlNm = os.path.join(binDir, itemNm + f".cp{MAJORMINORVER}-win_{ARCHI}.pyd")
            if os.path.isfile(targFlNm):
                os.remove(targFlNm)
            elif os.path.isdir(targFlNm):
                sh.rmtree(targFlNm)
            os.rename(origFlNm, targFlNm)

        except sp.CalledProcessError as e:
            reportCalledProcessError(e)
            return ERR_CALLEDPROCERR

        except PermissionError as e:
            reportPermErr(e, trace)
            return ERR_PERMDENIED

        except Exception as e:
            reportUnknErr(e, trace)
            return ERR_UNKNOWN

    return ERR_SUCCESS


def compileCore(env: dict[str, str], srcCoreDir: str, coreDir: str,
                srcBinDir: str, noasserts: bool, normdocstrs: bool,
                warn: bool, normout: bool, noquiet: bool, trace: bool,
                jobs: str, fls: list[str]) -> int:
    """
    Compiles the core interpreter files (files present in src\\core).
    > param env: Environment variables to use
    > param srcCoreDir: Source directory for core files
    > param coreDir: Build directory for core files
    > param srcBinDir: Source directory for bin files
    > param noasserts: Do not allow assertions
    > param normdocstrs: Do not remove docstrings
    > param warn: Do not suppress Python runtime warnings
    > param normout: Do not remove output (prog.build directory)
    > param noquiet: Do not suppress output
    > param trace: Print stack trace
    > param fls: Files to compile (empty to compile all)
    > return: Integer error code
    """
    fls = [os.path.basename(pl.Path(i).resolve()).lower() for i in fls]
    print(f"{BOLDGREEN}Using Python at {sys.executable} for CORE FILES{RESET}")

    for item in os.scandir(srcCoreDir):
        if not os.path.isfile(item):
            continue

        itemNm, itemExt = os.path.splitext(os.path.basename(item.path))
        if itemExt != ".py":
            continue

        if fls:
            if item.name.lower() not in fls:
                continue

        command = [
            sys.executable,
            "-OO",
            "-W",
            "error",
            "-m",
            "nuitka",
            "--module",
            "--include-module=ctypes",
            "--include-module=getpass",
            # f"--include-plugin-directory={srcBinDir}",
            "--python-flag=no_docstrings" if not normdocstrs else '',
            "--python-flag=-O" if noasserts else '',
            "--python-flag=no_warnings" if not warn else '',
            f"--jobs={jobs}" if jobs else '',
            "--remove-output" if not normout else '',
            "--no-pyi-file",
            f"--output-dir={coreDir}",
            "--quiet" if not noquiet else '',
            item.path
        ]
        command = [i for i in command if i]

        try:
            print(f"{BOLD}Execute:{RESET} {' '.join(command)}")
            sp.run(command, env=env, capture_output=True if not noquiet else False,
                   text=True, check=True)
            targFlNm = os.path.join(coreDir, itemNm + ".pyd")
            origFlNm = os.path.join(coreDir, itemNm + f".cp{MAJORMINORVER}-win_{ARCHI}.pyd")
            if os.path.isfile(targFlNm):
                os.remove(targFlNm)
            elif os.path.isdir(targFlNm):
                sh.rmtree(targFlNm)
            os.rename(origFlNm, targFlNm)

        except sp.CalledProcessError as e:
            reportCalledProcessError(e)
            return ERR_CALLEDPROCERR

        except PermissionError as e:
            reportPermErr(e, trace)
            return ERR_PERMDENIED

        except Exception as e:
            reportUnknErr(e, trace)
            return ERR_UNKNOWN

    return ERR_SUCCESS


def compileMain(env: dict[str, str], buildDir: str, coreDir: str, srcBinDir: str,
                binDir: str, fl: str, nostandalone: bool, noasserts: bool,
                normdocstrs: bool, warn: bool, normout: bool, noquiet: bool,
                trace: bool, jobs: str, icon: str | None = None) -> int:
    """
    Compiles the main program (file present in src).
    > param env: Environment variables to use
    > param buildDir: Build directory
    > param coreDir: Build directory for core files
    > param srcBinDir: Source directory for bin files
    > param binDir: Build directory for bin files
    > param fl: File to compile
    > param nostandalone: Do not use "standalone" mode, i.e. uses "onefile" mode
    > param noasserts: Do not allow assertions
    > param normdocstrs: Do not remove docstrings
    > param warn: Do not suppress Python runtime warnings
    > param normout: Do not remove output (prog.build directory)
    > param noquiet: Do not suppress output
    > param trace: Print stack trace
    > param icon: Icon to use for the program
    > return: Integer error code
    """
    try:
        for i in os.scandir(buildDir):
            if i.path in (coreDir, binDir):
                continue
            if os.path.isfile(i):
                os.remove(i)
            else:
                sh.rmtree(i)
    except PermissionError as e:
        reportPermErr(e, trace)
        return ERR_PERMDENIED

    nm, ext = os.path.splitext(os.path.basename(fl))
    if ext != ".py":
        reportInvFlType()
        return ERR_INVFLTYPE

    print(f"{BOLD + GREEN}Using Python at {sys.executable} for MAIN PROG{RESET}")

    command = [
        sys.executable,
        "-OO",
        "-W",
        "error",
        "-m",
        "nuitka",
        "--standalone" if not nostandalone else "--onefile",
        "--follow-imports",
        "--include-module=ctypes",
        "--lto=yes",
        "--noinclude-pytest-mode=nofollow",
        # f"--include-plugin-directory={srcBinDir}",
        "--python-flag=no_docstrings" if not normdocstrs else '',
        "--python-flag=-O" if noasserts else '',
        "--python-flag=no_warnings" if not warn else '',
        f"--jobs={jobs}" if jobs else '',
        f"--output-dir={buildDir}",
        "--remove-output" if not normout else '',
        "--no-pyi-file",
        "--quiet" if not noquiet else '',
        f"--windows-icon-from-ico={icon}" if icon is not None else '',
        str(pl.Path(fl).resolve())
    ]
    command = [i for i in command if i]

    try:
        distDir = os.path.join(buildDir, nm + f".dist")

        print(f"{BOLD}Execute:{RESET} {' '.join(command)}")
        sp.run(command, env=env, capture_output=True if not noquiet else False,
               text=True, check=True)

        if not nostandalone:
            sh.copytree(distDir, buildDir, dirs_exist_ok=True)
            sh.rmtree(distDir)
            print(f"{BOLD}INFO:{RESET} Built files copied from dist directory "
                  "to build directory")

    except sp.CalledProcessError as e:
        reportCalledProcessError(e)
        return ERR_CALLEDPROCERR

    except PermissionError as e:
        reportPermErr(e, trace)
        return ERR_PERMDENIED

    except Exception as e:
        reportUnknErr(e, trace)
        return ERR_UNKNOWN

    return ERR_SUCCESS


def main() -> None:
    args, err = parseArgs()

    if err:
        sys.exit(err)
    # Help message printed
    if not err and not args:
        sys.exit(0)

    normout          = args["normout"]
    nostandalone     = args["nostandalone"]
    noasserts        = args["noasserts"]
    normdocstrs      = args["normdocstrs"]
    noquiet          = args["noquiet"]
    warn             = args["warn"]
    trace            = args["trace"]
    run              = args["run"]
    jobs             = args["jobs"]
    fl               = args["fl"]
    icon             = args["icon"]
    nocompbin        = args["nocompbin"]
    nocompcore       = args["nocompcore"]
    nocompmain       = args["nocompmain"]
    noaliasesfile    = args["noaliasesfile"]
    nosettingsfile   = args["nosettingsfile"]
    noerrorcodesfile = args["noerrorcodesfile"]
    flnms            = args["flnms"]

    if fl is None:
        print(f"{BOLDRED}ERROR:{RESET} Argument file required for compilation")
        print("Use -h / --help for the help message")
        sys.exit(ERR_NOFL)

    env        = os.environ.copy()
    srcDir     = str(os.path.dirname(pl.Path(fl).resolve()))
    srcBinDir  = os.path.join(srcDir, "bin")
    srcCoreDir = os.path.join(srcDir, "core")
    buildDir   = os.path.join(srcDir, "build")
    binDir     = os.path.join(buildDir, "bin")
    coreDir    = os.path.join(buildDir, "core")
    aliasesFl  = os.path.join(srcDir, "_aliases.txt")
    settFl     = os.path.join(srcDir, "_settings.txt")
    errCodesFl = os.path.join(srcDir, "errCodes.txt")
    iconFl     = str(pl.Path(icon).resolve()) if icon is not None else None

    coreFls    = []
    binFls     = []
    flNmsErr   = False
    for i in flnms:
        i = str(pl.Path(i).resolve())

        if not os.path.isfile(i):
            print(f"{RED}ERROR:{RESET} Is a directory: \"{i}\"")
            flNmsErr = True
            continue

        if os.path.dirname(i) == srcCoreDir:
            coreFls.append(i)
        elif os.path.dirname(i) == srcBinDir:
            binFls.append(i)
        else:
            print(f"{RED}ERROR:{RESET} Is not a bin or core file: \"{i}\"")
            flNmsErr = True

    if flNmsErr:
        sys.exit(ERR_FLNMSERR)

    try:
        if not nocompmain:
            for i in os.scandir(buildDir):
                if i.path == coreDir and nocompcore or flnms:
                    continue
                if i.path == binDir and nocompbin or flnms:
                    continue
                if os.path.isfile(i):
                    os.remove(i)
                else:
                    sh.rmtree(i)
        if not nocompbin and not flnms:
            sh.rmtree(binDir)
        if not nocompcore and not flnms:
            sh.rmtree(coreDir)
    except FileNotFoundError:
        pass
    except PermissionError as e:
        reportPermErr(e, trace=True)
        sys.exit(ERR_PERMDENIED)
    finally:
        try:
            os.makedirs(buildDir, exist_ok=True)
            os.makedirs(binDir, exist_ok=True)
            os.makedirs(coreDir, exist_ok=True)
        except PermissionError as e:
            reportPermErr(e, trace=True)
            sys.exit(ERR_PERMDENIED)

    # Build bin files
    if not nocompbin:
        binErr = compileBin(env, srcBinDir, binDir, noasserts, normdocstrs,
                            warn, normout, noquiet, trace, jobs, binFls)
        if binErr:
            print(f"{BOLDRED}BUILD FAILED ATTEMPTING TO BUILD BIN FILES{RESET}")
            print(f"{BOLD}Return:{RESET} {binErr}")
            sys.exit(binErr)

    # Build core files
    if not nocompcore:
        coreErr = compileCore(env, srcCoreDir, coreDir, srcBinDir, noasserts,
                              warn, normdocstrs, normout, noquiet, trace, jobs,
                              coreFls)
        if coreErr:
            print(f"{BOLDRED}BUILD FAILED ATTEMPTING TO BUILD CORE FILES{RESET}")
            print(f"{BOLD}Return:{RESET} {coreErr}")
            sys.exit(coreErr)

    # Build main prog
    if not nocompmain:
        mainErr = compileMain(env, buildDir, coreDir, srcBinDir, binDir, fl,
                              nostandalone, noasserts, normdocstrs, warn, normout,
                              noquiet, trace, jobs, iconFl)
        if mainErr:
            print(f"{BOLDRED}BUILD FAILED ATTEMPTING TO BUILD MAIN PROG{RESET}")
            print(f"{BOLD}Return:{RESET} {mainErr}")
            sys.exit(mainErr)

    # Copy aliases file
    if not noaliasesfile:
        try:
            sh.copy2(aliasesFl, buildDir)
            print(f"{BOLD}INFO:{RESET} Alias file copied to build directory")
        except FileNotFoundError:
            print(f"{BOLDYELLOW}WARN:{RESET} File \"{aliasesFl}\" was not "
                  "found; skipping...")
        except PermissionError:
            print(f"{BOLDYELLOW}WARN:{RESET} Permission denied to copy "
                  f"\"{aliasesFl}\" to build directory; skipping...")

    # Copy settings file
    if not nosettingsfile:
        try:
            sh.copy2(settFl, buildDir)
            print(f"{BOLD}INFO:{RESET} Settings file copied to build "
                    "directory")
        except FileNotFoundError:
            print(f"{BOLDYELLOW}WARN:{RESET} File \"{settFl}\" was not "
                  "found; skipping...")
        except PermissionError:
            print(f"{BOLDYELLOW}WARN:{RESET} Permission denied to copy "
                  f"\"{settFl}\" to build directory; skipping...")

    # Copy error codes file
    if not noerrorcodesfile:
        try:
            sh.copy2(errCodesFl, buildDir)
            print(f"{BOLD}INFO:{RESET} Error codes file copied to build "
                    "directory")
        except FileNotFoundError:
            print(f"{BOLDYELLOW}WARN:{RESET} File \"{errCodesFl}\" was not "
                  "found; skipping...")
        except PermissionError:
            print(f"{BOLDYELLOW}WARN:{RESET} Permission denied to copy "
                  f"\"{errCodesFl}\" to build directory; skipping...")

    print(f"{BOLDGREEN}BUILD SUCCESSFUL{RESET}")

    # Run the output executable
    if run:
        nm, _ = os.path.splitext(fl)
        print(f"{BOLD}INFO:{RESET} RUNNING OUTPUT EXECUTABLE")
        try:
            os.chdir(buildDir)
            sp.run([os.path.join(buildDir, nm + ".exe")], env=env,
                    check=True, text=True)
        except sp.CalledProcessError as e:
            print(f"{BOLD}ERROR:{RESET} Program returned non-zero error code")
            sys.exit(ERR_RUNERR)
        except FileNotFoundError:
            print(f"{YELLOW}That's not supposed to happen...{RESET}")
            print(f"{BOLD}ERROR:{RESET} Program was not found")
            sys.exit(ERR_UNKNOWN)

    sys.exit(ERR_SUCCESS)


if __name__ == "__main__":
    main()
