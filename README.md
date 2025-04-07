# The Comet 1 Interpreter
Incomplete source code of the Comet 1 interpreter.<br>
Some aspects of the interpreter are yet to be completed, and some help strings require some work. But these are only minor changes, and the interpreter is stable enough to be used as such.<br>
Currently, it is available for Windows, and cannot be used with Linux due to it being extremely tailored for Windows. Linux source code will be released at a later point in time.

## Changes
The Comet interpreter has various changes over the last interpreter, Second 5, such as (and not included to):
 - Piping<br>
   The `|` operator.
 - Redirection<br>
   The `>` operator.
 - Logical operator support<br>
   The `&` (logical AND) and `^` (logical OR) operators.
 - Command separation<br>
   `;` can be used to separate multiple commands.
 - Extensible design<br>
   External commands can be modified or new external commands can be added.

## Running
Run as:
```
<python> -OO -B <path-to-main.py>
```

## Building
For now, building is not possible. Modules compiled with Nuitka does not seem to have a module export function (PyInit_func), which results in being unable to access external commands (built-in commands work just fine). Tried with Cython too, but with same result.<br>
<br>
I don't know how to fix this, so if you have any suggestions, please do contact me.

## Bug reporting
Please use the [Issues page](http://github.com/cpythonist/Comet1/issues) to report an bugs or typos encountered in the interpreter.

## Contribution
To contribute, please mail your patches to my email ID.
