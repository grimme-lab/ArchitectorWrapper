from pathlib import Path

from src import Mutator


def mutation():
    """
    Perform mutations on a series of compounds organized in separate folders.

    The function relies on the Mutator class to perform the mutations.
    It takes compounds from a directory, mutates them based on
    specified oxidation states, and saves them to an output directory.
    """
    # Input directory containing compounds in separate folders
    dir = Path(__file__).parent / "dummy"
    dir_out = Path(__file__).parent / "dummy_mutations"

    # Original and new oxidation states are manually required
    os = 3
    os_new = 3

    # Execute mutations
    mut = Mutator(dir, os, os_new, dir_out)
    mut.mutate()
