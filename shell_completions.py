#!/usr/bin/env python

import argparse, pexpect


COMPLETIONS_COMMAND = ". /etc/bash_completion"


def print_string(message, string):
    print message + " \"" + string + "\""


def get_completions(partial_command, command="bash", separator="\n", 
                    return_raw=False, import_completions=True, get_prompt=True):
    """
    Put a docstring here.
    """

    child = pexpect.spawn(command, timeout=5)

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

    index = child.expect_exact([" ", "\r\n", pexpect.TIMEOUT], timeout=1)

    if index == 0:
        # Bash found a single completion and filled it in.
        return child.before
    elif index == 1:
        # Bash found more than one completion and listed them on multiple lines.
        child.expect_exact(prompt)
        return child.before
    elif index == 2:
        # If the command timed out, either no completion was found or it
        # found a single completion witout adding a space (for instance, this 
        # happens when completing the name of an executable).

        # print_string("Timed out:", child.before)

        # Remove any bell characters bash emitted with the completion.
        return child.buffer.replace("\x07", "")

    child.close()


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(
		description="Return the completions that bash would suggest for the given input string.")

	parser.add_argument('separator', metavar='separator', type=str, nargs=1,
						help="Separation character used for the list of completions." )