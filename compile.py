import os
import shutil     as sh
import subprocess as sp


def compileCommandPyds():
    sh.rmtree("bin", ignore_errors=True)
    os.makedirs("bin", exist_ok=False)

    for name in os.scandir("bin_"):
        if not (os.path.isfile(name) and name.name.endswith(".py")):
            continue
        sp.run(("python", "-W", "ignore", "-OO", "-m", "nuitka", "--module",
                "--include-module=ctypes",
                "--quiet", "--remove-output", "--output-dir=bin", name.path))
        os.rename("bin" + os.sep + f"{name.name[:-3]}.cp312-win_amd64.pyd",
                  "bin" + os.sep + f"{name.name[:-3]}.pyd")
        os.remove("bin" + os.sep + name.name[:-3] + ".pyi")


def compileCorePyds():
    sh.rmtree("core", ignore_errors=True)
    os.makedirs("core", exist_ok=False)

    for name in os.scandir("core_"):
        if not (os.path.isfile(name) and name.name.endswith(".py")):
            continue
        if name.name not in ("comet.py", "commons.py"):
            continue
        sp.run(("python", "-W", "ignore", "-OO", "-m", "nuitka", "--module",
                "--output-dir=core", "--remove-output",
                "--quiet",
                "--include-module=ctypes", name.path))
        os.rename("core" + os.sep + f"{name.name[:-3]}.cp312-win_amd64.pyd",
                  "core" + os.sep + f"{name.name[:-3]}.pyd")
        os.remove("core" + os.sep + name.name[:-3] + ".pyi")


def compileMain():
    sh.rmtree("main.dist", ignore_errors=True)
    sp.run(("python", "-W", "ignore", "-OO", "-m", "nuitka", "--standalone",
            "--follow-import-to=comet", "--follow-import-to=commons",
            "--include-module=ctypes", "--remove-output",
            "--quiet",
            "main.py"))


def copyBinAndCore():
    sh.rmtree("main.dist\\bin", ignore_errors=True)
    sh.rmtree("main.dist\\core", ignore_errors=True)
    sh.copytree("bin", "main.dist\\bin")
    sh.copytree("core", "main.dist\\core")


compileCommandPyds()
compileCorePyds()
compileMain()
copyBinAndCore()
