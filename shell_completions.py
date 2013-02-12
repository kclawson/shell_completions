#!/usr/bin/env python

import argparse, pexpect, sys


COMPLETIONS_COMMAND = ". /etc/bash_completion"
BIGLIST_WARNING = "(y or n)"
NEXT_PAGE_INDICATOR = "--More--"


def print_string(message, string):
    print message + " \"" + string + "\""


def completions(partial_command, command="bash", return_raw=False, 
                import_completions=True, get_prompt=True, timeout=2, 
                biglist=True, verbose=False):
    """
    Returns a list containing the tab completions found by the shell for the 
    input string.
    """

    child = pexpect.spawn(command, timeout=timeout)

    if verbose:
        child.logfile = sys.stdout

    #### NOTE: It would be nice to disable the echo, but for some reason things
    ####       go haywire without it.
    # child.setecho(False)

    # Get a bare command prompt in order to find the end of the
    # list of completions.
    if get_prompt:
        child.sendline()
        child.expect_exact("\r\n")
        child.expect_exact("\r\n")
        prompt = child.before
        if verbose:
            print_string("Prompt:", prompt)

    # Run a script to configure extra bash completions.
    if import_completions:
        child.sendline(COMPLETIONS_COMMAND)
        child.expect_exact(prompt)
        child.expect_exact(prompt)

    child.send(partial_command + "\t\t")
    child.expect_exact(partial_command)
    #### NOTE: I don't understand why this time we don't get an echo.
    # child.expect_exact(partial_command)

    index = child.expect_exact([" ", "\r\n", pexpect.TIMEOUT])

    if index == 0:
        # Bash found a single completion and filled it in.
        return [partial_command + child.before]
    elif index == 1:
        index = child.expect_exact([BIGLIST_WARNING, prompt])
        if index == 0:
            # Shell found many possibilities and asks whether to continue.
            if biglist:
                child.send("y")
                completions = ""
                while True:
                    index = child.expect_exact([prompt, NEXT_PAGE_INDICATOR])
                    if index == 0:
                        break
                    elif index == 1:
                        completions += child.before
                        child.send(" ")
        elif index == 1:
            # Bash found more than one completion and listed them on multiple lines.
            # child.expect_exact(prompt)
            completions = child.before
    elif index == 2:
        # If the command timed out, either no completion was found or it
        # found a single completion witout adding a space (for instance, this 
        # happens when completing the name of an executable).

        # print_string("Timed out:", child.before)

        # Remove any bell characters the shell appended to the completion.
        return [partial_command + child.buffer.replace("\x07", "")]
    
    child.close()

    # Parse the completions into a Python list of strings.
    return completions.split()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Returns the tab completions found by the shell for the input string.")

    parser.add_argument("COMMAND", type=str,
                        help="The partial command that the shell should attempt to complete.")

    parser.add_argument("--separator", default="\n",
                        help="Character used to separate the list of completions.")

    args = parser.parse_args()

    completion_list = completions(args.COMMAND)

    print str(args.separator).join(completion_list)