This is a small Python script that returns the list of command-line tab completions
for an input string.

Usage
-----
`shell_completions.py [-h] [--separator SEPARATOR] COMMAND`

Positional arguments
--------------------

 - **COMMAND**               The partial command that the shell should attempt to
                         complete.

Optional arguments
------------------
  - **-h, --help**            Show this help message and exit.
  - **--no_biglists**         Abort execution if the shell finds a large number of
                          completions.
  - **--no_detect_prompt**    Don't attempt to detect the command prompt, and use a
                          built-in constant instead. This should speed up
                          execution times.
  - **--no_import_completions** NO_IMPORT_COMPLETIONS
                          Don't set up completions by running the script at
                          /etc/completions.
  - **--raw**                 Returns all output from the shell without formatting
                          changes.
  - **--separator SEPARATOR, -s SEPARATOR**
                          Character used to separate the list of completions.
  - **--shell SHELL**         The shell to query for completions. Defaults to bash.
  - **--timeout SECONDS, -t SECONDS**
                          The time in seconds before the program detects no
                          shell output.
  - **--verbose, -v**         Verbose mode.
