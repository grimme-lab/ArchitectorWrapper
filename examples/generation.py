from pathlib import Path

from src import SampleDataset


def generate_dataset():
    """
    Generates a dataset containing complexes with a single central atom species.

    This function creates a dataset that includes complexes with a single specified central atom species, along with
    various oxidation states, spin states, coordination numbers, and other settings.
    """

    # Define the path to save the dataset
    dataset_save_path = Path(__file__).parent / "dummy.json"

    # Generate the dataset with the specified parameters
    dataset = SampleDataset.generate(
        central_atom="La",
        central_atom_OS=3,
        central_atom_spin=0,
        n_complexes=3,
        min_CN=5,
        max_CN=9,
    )

    # Write the generated dataset to the specified path
    dataset.write(dataset_save_path)


def generate_multi_atom_dataset():
    """
    Generates a dataset with complexes containing different central atoms and coordinating geometries.

    This function creates a dataset that includes complexes with various central atoms and coordination numbers,
    oxidation states, and spin states. It's designed to automatically generate large and diverse datasets with
    predefined settings.
    """

    # Define the path to save the dataset
    dataset_save_path = Path(__file__).parent / "dummy_multi.json"

    # Configuration for the first set of complexes
    cfg1 = {
        "central_atom": "La",
        "central_atom_OS": 3,
        "central_atom_spin": 0,
        "n_complexes": 8,
        "min_CN": 5,
        "max_CN": 9,
    }

    # Configuration for the second set of complexes
    cfg2 = {
        "central_atom": "Zn",
        "central_atom_OS": 2,
        "central_atom_spin": 0,
        "n_complexes": 10,
        "min_CN": 3,
        "max_CN": 7,
    }

    # Combine configurations
    cfgs = [cfg1, cfg2]

    # Generate the dataset for the first configuration
    dataset = SampleDataset.generate(**cfgs[0])

    # Generate and combine datasets for the rest of the configurations
    for params_dict in cfgs[1:]:
        dataset = dataset + SampleDataset.generate(**params_dict)

    # Write the generated dataset to the specified path
    dataset.write(dataset_save_path)
