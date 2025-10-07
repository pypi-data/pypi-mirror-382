# Beepper

[![PyPI downloads](https://img.shields.io/pypi/dm/beepper.svg)](https://pypi.org/project/beepper/)

Simple interface to create an alert noise. Might cause a [silent crash](https://github.com/hamiltron/py-simple-audio/issues/72) after the sound has stopped playing when using python 3.12.

### Installation with pip

Running the command:

    python -m pip install beepper

in a terminal will install the package to the active environment.

### Usage

Has a parameter `vol` for setting the volume and a parameter `blocking` to optionally make the function blocking.

Example usage in a project:

    from beepper import beep

    for i in seq:
        do_something(i)

    beep(1.5)

    do_something_else()

In the example, beep gets called after the loop. The function `do_something_else` gets called while the beep is still running in the backround.

The sound can also be played in a blocking manner. By calling the function with an additional argument `beep(1.5, True)`, the program waits until the sound has stopped playing until the next line gets executed.
