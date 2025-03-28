import os
import sys
import argparse   as ap
import shutil     as sh
import subprocess as sp
import traceback  as tb

BOLD      = "\033[1m"
BLINK     = "\033[5m"
BLUE      = "\033[94m"
CYAN      = "\033[96m"
GREEN     = "\033[92m"
RED       = "\033[91m"
RESET     = "\033[0m"
UNDERLINE = "\033[4m"
YELLOW    = "\033[93m"


def reportCalledProcessError(e: sp.CalledProcessError) -> None:
    print(f"{BOLD + RED}FAIL:{RESET} Build failed on command: {' '.join(e.cmd)}")
    print(f"{BOLD + CYAN}STDOUT:{RESET}{('\n' + e.stdout) if e.stdout else ''}")
    print(f"{BOLD + RED}STDERR:{RESET}{('\n' + e.stderr) if e.stderr else ''}")


def compileBin(env: dict[str, str], normout: bool, noquiet: bool,
               warnings: str, noremovecomments: bool) -> int:
    """
    Compiles the command files (present in src\\bin).
    > param env: Environment variables to use
    > param normout: Do not remove output (prog.build directory)
    > param noquiet: Do not suppress output
    > param warnings: Warning level
    > param noremovecomments: Do not remove comments (docstrings)
    > return: Error code
          -1: Unknown error
          +0: Success
          +1: CalledProcessError (Error during execution of the command)
          +2: Permission error
    """
    if os.path.isdir(os.path.join("build", "bin")):
        sh.rmtree(os.path.join("build", "bin"), ignore_errors=False)

    print(f"{BOLD + GREEN}Using Python at {sys.executable} for BIN FILES{RESET}")

    for item in os.scandir("bin"):
        if not os.path.isfile(item):
            continue

        command = [
            sys.executable,
            "-OO" if not noremovecomments else '',
            "-W",
            warnings,
            "-m",
            "nuitka",
            "--module",
            "--include-module=ctypes",
            "--include-plugin-directory=bin",
            "--python-flag=no_docstrings",
            "--remove-output" if not normout else '',
            f"--output-dir=build{os.sep}bin",
            "--quiet" if not noquiet else '',
            item.path
        ]
        command = [i for i in command if i]

        try:
            print(f"Execute: {' '.join(command)}")
            sp.run(command, env=env, capture_output=True if not noquiet else False,
                   text=True, check=True)
            os.rename(f"build{os.sep}bin" + os.sep + f"{item.name[:-3]}.cp312-win_amd64.pyd",
                      f"build{os.sep}bin" + os.sep + f"{item.name[:-3]}.pyd")
            os.remove(f"build{os.sep}bin" + os.sep + item.name[:-3] + ".pyi")

        except sp.CalledProcessError as e:
            reportCalledProcessError(e)
            return 1

        except PermissionError as e:
            print(f"({e.__class__.__name__}) {e}")
            return 2

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"({e.__class__.__name__}) {e}")
            return -1

    return 0


def compileCore(env: dict[str, str], normout: bool, noquiet: bool,
                warnings: str, noremovecomments: bool) -> int:
    """
    Compiles the core interpreter and other core files (present in src\\core).
    > param env: Environment variables to use
    > param normout: Do not remove output (prog.build directory)
    > param noquiet: Do not suppress output
    > param warnings: Warning level
    > param noremovecomments: Do not remove comments (docstrings)
    > return: Error code
          -1: Unknown error
          +0: Success
          +1: CalledProcessError (Error during execution of the command)
          +2: Permission error
    """
    if os.path.isdir(os.path.join("build", "core")):
        sh.rmtree(os.path.join("build", "core"), ignore_errors=False)

    print(f"{BOLD + GREEN}Using Python at {sys.executable} for CORE FILES{RESET}")

    for fileOrDir in os.scandir("core"):
        if not os.path.isfile(fileOrDir):
            continue

        try:
            command = [
                sys.executable,
                "-OO" if not noremovecomments else '',
                "-W",
                warnings,
                "-m",
                "nuitka",
                "--module",
                "--include-module=ctypes",
                "--include-plugin-directory=bin",
                "--python-flag=no_docstrings",
                "--remove-output" if not normout else '',
                f"--output-dir=build{os.sep}core",
                "--quiet" if not noquiet else '',
                fileOrDir.path
            ]
            command = [i for i in command if i]
            print(f"Execute: {' '.join(command)}")
            sp.run(command, env=env, capture_output=True if not noquiet else False,
                   text=True, check=True)
            os.rename(f"build{os.sep}core" + os.sep + f"{fileOrDir.name[:-3]}.cp312-win_amd64.pyd",
                      f"build{os.sep}core" + os.sep + f"{fileOrDir.name[:-3]}.pyd")
            os.remove(f"build{os.sep}core" + os.sep + fileOrDir.name[:-3] + ".pyi")

        except sp.CalledProcessError as e:
            reportCalledProcessError(e)
            return 1

        except PermissionError as e:
            print(f"({e.__class__.__name__}) {e}")
            return 2

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"({e.__class__.__name__}) {e}")
            return -1

    return 0


def compileMainProg(env: dict[str, str], file: str, normout: bool,
                    nofollowimports: bool, noquiet: bool, warnings: str,
                    noremovecomments: bool, nostandalone: bool) -> int:
    """
    > return: Error code:
          0: Success
          1: CalledProcessError (An error occured while running the command)
          2: Permission error
          -1: Unknown error
    """
    try:
        for i in os.scandir("build"):
            if i.name == "core" or i.name == "bin":
                continue
            if os.path.isfile(i):
                os.remove(i)
            else:
                sh.rmtree(i)

        print(f"{BOLD + GREEN}Using Python at {sys.executable} for MAIN PROG{RESET}")

        command = [
            sys.executable,
            "-OO" if not noremovecomments else '',
            "-W",
            warnings,
            "-m",
            "nuitka",
            "--standalone" if not nostandalone else "--onefile",
            "--include-module=ctypes",
            "--include-plugin-directory=bin",
            "--python-flag=no_docstrings",
            "--quiet" if not noquiet else '',
            "--output-dir=build",
            "--remove-output" if not normout else '',
            "--follow-imports" if not nofollowimports else '',
            file
        ]
        command = [i for i in command if i]
        print(f"Execute: {' '.join(command)}")
        sp.run(command, env=env, capture_output=True if not noquiet else False,
               text=True, check=True)

        os.system("move build" + os.sep + file[:-3] + ".dist\\* build")

        return 0

    except sp.CalledProcessError as e:
        reportCalledProcessError(e)
        return 1

    except PermissionError as e:
        print(f"({e.__class__.__name__}) {e}")
        return 2

    except Exception as e:
        print(f"({e.__class__.__name__}) {e}")
        return -1


built  = False
try:
    env    = os.environ.copy()
    parser = ap.ArgumentParser()

    parser.add_argument("file", help="Main program file to compile")
    parser.add_argument("-nro", "--normout", help="Remove output (prog.build)",
                        action="store_true", default=False)
    parser.add_argument("-nfi", "--nofollowimports", help="Do not follow imports",
                        action="store_true", default=False)
    parser.add_argument("-nq", "--noquiet", help="Do not quiet compile",
                        action="store_true", default=False)
    parser.add_argument("-w",  "--warnings", "--warn", help="Enable warnings",
                        default="error", choices=["ignore", "default", "error"],
                        type=str.lower)
    parser.add_argument("-nrc", "--noremovecomments", help="Remove comments",
                        action="store_true", default=False)
    parser.add_argument("-ns", "--nostandalone", help="Nuitka standalone option",
                        action="store_true", default=False)
    parser.add_argument("-r", "--run", help="Run the compiled program",
                        action="store_true", default=False)
    parser.add_argument("-ra", "--runargs", help="Arguments to pass to the program",
                        default="", type=str)

    args = parser.parse_args()

    if os.path.isdir("build"):
        sh.rmtree("build", ignore_errors=False)

    errBin = compileBin(env, args.normout, args.noquiet, args.warnings,
                        args.noremovecomments)
    if errBin:
        print(f"Failed trying to compile BIN FILES; return code {errBin}")
        sys.exit(errBin)

    errCore = compileCore(env, args.normout, args.noquiet, args.warnings,
                          args.noremovecomments)
    if errCore:
        print(f"Failed trying to compile CORE FILES; return code {errCore}")
        sys.exit(errCore)

    errMainProg = compileMainProg(env, args.file, args.normout,
                                  args.nofollowimports, args.noquiet,
                                  args.warnings, args.noremovecomments,
                                  args.nostandalone)
    if errMainProg:
        print(f"Failed trying to compile the MAIN PROGRAM; return code {errMainProg}")
        sys.exit(errMainProg)

    sh.rmtree(f"build\\{''.join(os.path.basename(args.file).split('.')[:-1])}.dist", ignore_errors=False)
    built = True
    print(f"{BOLD + GREEN}Build successful{RESET}")
    if args.run:
        if args.nostandalone:
            print(f"Execute: {os.path.join('.', "main.exe")}", args.runargs)
            os.system(f"{os.path.join('.', "main.exe")} {args.runargs}")
        else:
            print(f"Execute: cd \"{''.join(args.file.split('.')[:-1])}.dist\"")
            os.chdir(f"{''.join(args.file.split('.')[:-1])}.dist")
            print(f"Execute: {os.path.join('.', ''.join(args.file.split('.')[:-1]) + ".exe")} {args.runargs}")
            os.system(f".{os.sep}{''.join(args.file.split('.')[:-1])}.exe {args.runargs}")

except (KeyboardInterrupt, EOFError):
    print(f"{BOLD + RED}Build cancelled{RESET}") if not built else None
    sys.exit(-2)

except Exception as e:
    print(f"{BOLD + RED}Unknown error:{RESET}")
    tb.print_exc()
    sys.exit(-3)
