import json
from pathlib import Path

from .complex import Complex
from .ligand import Ligand
from .util import get_random_CN


class Sample:
    """
    Represents a sample with its core structure, ligands, and parameters.
    Essentially a string representation of a `Complex`.
    """

    def __init__(
        self,
        uid: str,
        core: dict[str, int],
        ligands: list[dict[str, list[int]]],
        parameters: dict[str, int],
    ) -> None:
        """
        Initializes a `Sample` instance.

        Args:
            uid (str): Unique identifier for the sample.
            core (dict[str, int]): Core element and core coordination number.
            ligands (list[dict[str, list[int]]]): Collection of ligands, each specified via SMILES,
                coordination list, and ligand type.
            parameters (dict[str, int]): Configuration including central atom oxidation state and total spin.
        """
        self.uid = uid
        self.core = core
        self.ligands = ligands
        self.parameters = parameters

    def to_dict(self) -> dict:
        """
        Converts the Sample instance to a dictionary representation.
        Omits the UID.

        Returns:
            dict: A dictionary containing core, ligands, and parameters.
        """
        return {
            "core": self.core,
            "ligands": self.ligands,
            "parameters": self.parameters,
        }


class SampleDataset:
    """
    Represents a collection of samples in a dataset.
    """

    json_file: str = "ligands.json"
    """File containing all available ligands."""

    def __init__(self, samples: list[Sample]) -> None:
        """
        Initializes a SampleDataset instance.

        Args:
            samples (list[Sample]): List of samples in the dataset.
        """
        self.samples = samples

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.

        Returns:
            int: Number of samples.
        """
        return len(self.samples)

    def __getitem__(self, idx: int) -> Sample:
        """
        Retrieves a sample from the dataset at the given index.

        Args:
            idx (int): Index of the sample to retrieve.

        Returns:
            Sample: The sample at the specified index.
        """
        return self.samples[idx]

    def __str__(self) -> str:
        """
        Returns a string representation of the SampleDataset.

        Returns:
            str: String representation of object.
        """
        return f"SampleDataset:{self.to_dict()}"

    def __add__(self, other):
        if isinstance(other, SampleDataset):
            return SampleDataset(self.samples + other.samples)
        raise ValueError("Can only add two SampleDataset instances")

    def contains(self, uid: str) -> bool:
        """
        Checks if a sample with a given UID is present in the dataset.

        Args:
            uid (str): Unique identifier of the sample.

        Returns:
            bool: True if the UID is found, otherwise False.
        """
        return uid in [s.uid for s in self.samples]

    def to_dict(self) -> dict:
        """
        Converts the SampleDataset instance to a dictionary representation.

        Returns:
            dict: Dictionary containing samples' UID as keys and their dictionary representations as values.
        """
        return {s.uid: s.to_dict() for s in self.samples}

    def write(self, path: str | Path) -> None:
        """
        Saves the dataset to a JSON file at the given path.

        Args:
            path (str): Path to the JSON file.
        """
        dd = self.to_dict()
        with open(path, "w") as json_file:
            json.dump(dd, json_file, indent=4)

    @staticmethod
    def read(path: str | Path) -> "SampleDataset":
        """
        Reads a dataset saved in JSON format from the given path.

        Args:
            path (str): Path to the JSON file.

        Returns:
            SampleDataset: The loaded SampleDataset instance.
        """
        with open(path, "r") as json_file:
            dd = json.load(json_file)

        return SampleDataset(samples=[Sample(uid=k, **v) for k, v in dd.items()])

    def add_sample(self, sample: Sample) -> None:
        """
        Add a single `Sample` to dataset. Sample will be added as last element in
        `dataset.samples`.

        Args:
            sample (Sample): Sample object to be added to dataset.
        """
        self.samples.append(sample)

    def remove_samples(self, keys: list[str]) -> None:
        """
        Removes samples from the dataset using their unique IDs.

        Args:
            keys (list[str]): List of UIDs of samples to be removed.
        """
        self.samples = [s for s in self.samples if s.uid not in keys]

    @staticmethod
    def generate(
        central_atom: str,
        central_atom_OS: int,
        central_atom_spin: int,
        n_complexes: int,
        min_CN: int,
        max_CN: int,
    ) -> "SampleDataset":
        """Generate the dataset containing the requested number of complexes (n_complexes),
        all having identical central atom in specific oxidation and spin states.

        Args:
            central_atom (str): Central atom's symbol.
            central_atom_OS (int): Central atom's oxidation state.
            central_atom_spin (int): Spin multiplicity of the central atom (2S+1).
            n_complexes (int): Number of unique complexes in the dataset.
            min_CN (int): Minimum coordination number.
            max_CN (int): Maximum coordination number.

        Returns:
            dict: Dictionary contating complex unique ids (hashes) as keys and inputDicts as values for every complex.
            The number of elements is equal to n_complexes.
        """

        with open(SampleDataset.json_file, "r") as file:
            all_ligands = json.load(file)

        dataset = SampleDataset([])

        # loop to generate the requested number of complexes
        while len(dataset) < n_complexes:
            # random CN generation
            entry = Complex(
                central_atom=central_atom,
                central_atom_OS=central_atom_OS,
                central_atom_spin=central_atom_spin,
                CN=get_random_CN(low=min_CN, high=max_CN + 1),
            )

            # loop to fill the coordination sites with random ligands
            while entry.complex_ready == False:
                random_ligand_dict, random_ligand_key = Ligand.get_random(all_ligands)

                remaining_coord_site = entry.get_remaining_coord_site_number()

                ligand_denticity = Ligand(**random_ligand_dict).denticity

                if ligand_denticity > remaining_coord_site:
                    continue

                elif remaining_coord_site == 0:
                    break

                else:
                    entry.add_ligand(
                        ligand_dict=random_ligand_dict, ligand_key=random_ligand_key
                    )

            if dataset.contains(entry.complex_uid):
                continue

            inputDict = entry.get_inputDict()
            inputDict = entry.set_atom_parameters(
                inputDict=inputDict,
                metal_ox=central_atom_OS,
                full_spin=central_atom_spin,
            )
            inputDict["uid"] = entry.complex_uid

            dataset.add_sample(Sample(**inputDict))

        return dataset
