shell_completions
=================

A small Python script that returns the list of command-line tab completions.

usage: shell_completions.py [-h] [--separator SEPARATOR] COMMAND

Returns the tab completions found by the shell for the input string.

positional arguments:
  COMMAND               The partial command that the shell should attempt to
                        complete.

optional arguments:
  -h, --help            show this help message and exit
  --separator SEPARATOR
                        Character used to separate the list of completions.
