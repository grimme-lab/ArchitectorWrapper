from pathlib import Path

from src import SampleDataset
from src import Optimiser


def optimisation():
    """Run batch optimisation of dataset. This creates
    .xyz geometries from a given `SampleDataset`."""

    # load samples from disk
    dataset = SampleDataset.read(Path(__file__).parent / "dummy.json")

    # Define the path to save the optimised structures
    opt_save_path = Path(__file__).parent / "dummy_opt"

    # Define settings for Arcitector.build_complex()
    # see details at https://github.com/lanl/Architector
    settings = {
        "full_method": "UFF",
        "assemble_method": "UFF",
        "n_conformers": 1,
        "relax": True,
        "return_only_1": True,
    }

    opt = Optimiser(opt_save_path, settings)
    opt.run(dataset)


def optimisation_parallel():
    """Run parallel optimisation of dataset. This creates
    .xyz geometries from a given `SampleDataset`."""

    # load samples from disk
    dataset = SampleDataset.read(Path(__file__).parent / "dummy.json")

    # Define the path to save the optimised structures
    opt_save_path = Path(__file__).parent / "dummy_parallel"

    # Define settings for Arcitector.build_complex()
    # see details at https://github.com/lanl/Architector
    settings = {
        "full_method": "UFF",
        "assemble_method": "UFF",
        "n_conformers": 1,
        "relax": True,
        "return_only_1": True,
    }

    opt = Optimiser(opt_save_path, settings, nprocs=3)
    opt.run(dataset)
