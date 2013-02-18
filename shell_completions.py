#!/usr/bin/env python

# Known bugs/oddities:
#   [X] Fails to correctly detect the prompt with certain .bashrc settings.
#   [X] Spurious empty strings/escape sequences appear with multi-page output.
#   [ ] Output is not consistent. Example: 'git stat' returns 'git status', while
#       'git sta' returns a list of completions only for the 'sta' part of the 
#       command.

import argparse, pexpect, sys

COMPLETIONS_COMMAND = ". /etc/bash_completion"
COMPLETIONS_COMMAND_TIMEOUT = 1
BIGLIST_WARNING = "(y or n)"
NEXT_PAGE_INDICATOR = "--More--"
DEFAULT_TIMEOUT=0.1
DEFAULT_SHELL="bash --norc"
DEFAULT_PROMPT="bash-4.2$ "
BEEP="\x07"
NEWLINE="\r\n"


def print_string(message, string):
    print message + " \"" + string + "\""


def completions(partial_command, shell=DEFAULT_SHELL, return_raw=False, 
                import_completions=True, set_prompt=False, prompt=None,
                timeout=DEFAULT_TIMEOUT, biglist=True, verbose=False,
                logfile=None):
    """
    Returns a list containing the tab completions found by the shell for the 
    input string.
    """
    if prompt is None:
        prompt = DEFAULT_PROMPT

    child = pexpect.spawn(shell, timeout=timeout)
    child.expect_exact(prompt)

    if logfile is not None:
        logfile = open(logfile, "w")
        child.logfile = logfile 

    if verbose:
        print_string("Python version:", sys.version)
        print_string("Echo state:", child.getecho())
        # child.logfile = sys.stdout

    # Run a script to configure extra bash completions.
    if import_completions:
        child.sendline(COMPLETIONS_COMMAND)
        child.expect_exact(prompt, timeout=COMPLETIONS_COMMAND_TIMEOUT)
        
    child.send(partial_command + "\t\t")

    index = child.expect_exact([BEEP, pexpect.TIMEOUT])
 
    if index == 0:
        # Shell beeped at us. It will always beep at least once when it receives the second
        # tab character.

        if verbose:
            print "BEFORE: " + child.before
            print "PARTIAL: " + partial_command

        # Shell beeped before printing any completions.
        if child.before == partial_command:
            
            index = child.expect_exact([BEEP, NEWLINE])
            
            if index == 0:
                # The completion fit on one line.
                return [partial_command + child.before]
            
            elif index == 1:
                # The completion required multiple lines.

                index = child.expect_exact([BIGLIST_WARNING, NEXT_PAGE_INDICATOR, prompt])
                if index == 0 or index == 1:
                    # The shell found so many completions that we must page through them.
                    if biglist:
                        completions = ""

                        # For very long lists the shell asks whether to continue.
                        if index == 0:
                            child.send("y")
                        
                        # Shorter lists print to the screen without asking. 
                        else:
                            completions += child.before
                            child.send(" ")
                        
                        # Keep sending space to get more pages until we get back to the 
                        # command prompt.
                        while True:
                            index = child.expect_exact([NEXT_PAGE_INDICATOR, prompt])
                            completions += child.before
                            if index == 0:
                                child.send(" ")
                            elif index == 1:
                                break
                        
                        # Remove spurious escape sequence.
                        completions = completions.replace("\x1b[K", "").split()

                elif index == 2:
                    # The completions required multiple lines, but still fit on one page.
                    completions = child.before.split()

        else:
            # Shell beeped at the end of the completion. This happens when a single completion
            # is found and the shell automatically fills it in.
            completions = [child.before]

    elif index == 1:
        # Timed out. 
        # Either there was no completion found, or it took too long to search.
        completions = [""]

    child.close()

    return completions 


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Returns the tab completions found by the shell for the input string.")

    parser.add_argument("COMMAND", type=str,
                        help="The partial command that the shell should attempt to complete.")

    parser.add_argument("--no_biglists", action="store_false", default=True,
                        help="Abort execution if the shell finds a large number of completions.")

    parser.add_argument("--prompt", default=None,
                        help="Don't attempt to detect the command prompt, and use a built-in constant instead. This should speed up execution times.")

    parser.add_argument("--no_import_completions", default=True,
                        help="Don't set up completions by running the script at /etc/completions.")
    parser.add_argument("--raw", action="store_false", default=False,
                        help="Returns all output from the shell without formatting changes.")

    parser.add_argument("--separator", "-s", default="\n",
                        help="Character used to separate the list of completions.")

    parser.add_argument("--shell", default="bash",
                        help="The shell to query for completions. Defaults to bash.")

    parser.add_argument("--timeout", "-t", metavar="SECONDS", type=float, default=DEFAULT_TIMEOUT,
                        help="The time in seconds before the program detects no shell output.")

    parser.add_argument("--verbose", "-v", action="store_true", default=False,
                        help="Verbose mode.")

    parser.add_argument("--log", "-l", metavar="LOGFILE", default=None,
                        help="Log all shell output to file named LOGFILE.")

    args = parser.parse_args()

    completion_list = completions(args.COMMAND, verbose=args.verbose, 
        return_raw=args.raw, timeout=args.timeout, biglist=args.no_biglists, 
        prompt=args.prompt, logfile=args.log)

    print str(args.separator).join(completion_list)