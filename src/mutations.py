import pandas as pd
from pathlib import Path

from .constants import lanthanides, actinides, ln_multiplicity, ac_multiplicity
from .io import save_chrg, save_uhf, save_xyz
from .util import read_xyz, check_max_one_overlap


class Mutator:
    dir: Path
    """Directory containing all compounds in subfolders."""

    oxidation_state: int
    """Original oxidation state of central atom."""

    oxidation_state_new: int
    """New oxidation state of central atom."""

    outdir: Path | None
    """Directory containing all mutated compounds."""

    xyz_file: str = "sample.xyz"
    """Naming scheme for .xyz files."""

    chrg_file: str = ".CHRG"
    """Naming scheme for charge files."""

    uhf_file: str = ".UHF"
    """Naming scheme for unpaired electrons files."""
    # NOTE: naming schemes are used for both original and mutated compounds

    def __init__(
        self,
        dir: Path,
        oxidation_state: int,
        oxidation_state_new: int,
        outdir: Path = None,
    ) -> None:
        self.dir = dir
        self.oxidation_state = oxidation_state
        self.oxidation_state_new = oxidation_state_new
        self.outdir = outdir

        if self.outdir == None:
            self.outdir == self.dir
        self.outdir.mkdir(parents=True, exist_ok=True)

    def mutate(self) -> None:
        """
        Iterate through each sub-directory in the parent directory and mutate the compounds within.
        """
        # avoid IO issues for self.outdir == self.dir
        for fp in [f for f in self.dir.iterdir()]:
            if fp.is_dir():
                self.mutate_compound(fp)

    def mutate_compound(self, dir: Path) -> None:
        """
        Mutate a single compound based on the .xyz and .CHRG files in the given directory.

        Args:
            dir (Path): The directory containing the sample files (sample.xyz, sample.CHRG).

        Raises:
            ValueError: If the required files with extensions .xyz and .CHRG are not found.
        """

        for file in [self.xyz_file, self.chrg_file, self.uhf_file]:
            if not (dir / file).exists():
                raise IOError(f"Required file {file} not found in {dir}")

        elements, _ = read_xyz(dir / self.xyz_file)

        # check for mono-complex
        _all = lanthanides + actinides
        assert check_max_one_overlap(
            _all, elements
        ), "More than one central atom present"

        # automatically detect central atom
        central_atom = set(_all).intersection(set(elements)).pop()

        # permute other elements
        if central_atom in lanthanides:
            elements_to_permute = lanthanides.copy()
        elif central_atom in actinides:
            elements_to_permute = actinides.copy()
        else:
            raise ValueError("Only lanthanides and actinides supported.")

        elements_to_permute.remove(central_atom)

        for element in elements_to_permute:
            # Assume each compound saved by uid (uid == dir)
            uid = self.mutated_uid(str(dir.name), element)

            # Create output in same folder
            outdir = self.outdir / uid
            outdir.mkdir(parents=True, exist_ok=True)

            # Perform mutations and save new files
            self.mutate_xyz(
                xyz_to_mutate=str(dir / self.xyz_file),
                old_CA=central_atom,
                new_CA=element,
                save_path=str(outdir / self.xyz_file),
            )
            self.mutate_chrg(
                chrg_to_mutate=str(dir / self.chrg_file),
                old_OS=self.oxidation_state,
                new_OS=self.oxidation_state_new,
                save_path=str(outdir / self.chrg_file),
            )
            new_unpels = (
                self.calc_multiplicity(CA=element, OS=self.oxidation_state_new) - 1
            )
            save_uhf(new_unpels, str(outdir / self.uhf_file))

    def mutate_xyz(
        self, xyz_to_mutate: str, old_CA: str, new_CA: str, save_path: str
    ) -> None:
        """
        Mutate the atomic species in an XYZ file and save the mutated file to a new location.

        Args:
            xyz_to_mutate (str): Path to the original XYZ file that needs to be mutated.
            old_CA (str): The initial central atom (element symbol) to be replaced.
            new_CA (str): The new central atom (element symbol) to replace the old central atom.
            save_path (str): The path where the new mutated XYZ file will be saved.

        Raises:
            IOError: If the file path provided does not end with .xyz.
            ValueError: If the element symbols are not correctly capitalized.

        Returns:
            None: This function saves the mutated XYZ file but does not return any value.
        """
        new_lines = []

        if not xyz_to_mutate.endswith(".xyz"):
            raise IOError("This must be a path to .xyz file!")

        if old_CA.islower() or new_CA[0].islower():
            raise ValueError("The element symbols must begin with a capital letter!")

        with open(xyz_to_mutate, "r") as file:
            all_lines = file.readlines()

            for i, line in enumerate(all_lines):
                if i in [0, 1]:
                    new_lines.append(line)
                    continue

                splitted_line = [x for x in line.strip().split()]

                if old_CA in splitted_line:
                    mutated_line = splitted_line
                    mutated_line[0] = new_CA
                    mutated_line.append("\n")
                    mutated_string = ("  ").join(mutated_line)
                    new_lines.append(mutated_string)

                else:
                    new_lines.append(line)
                    continue

        with open(save_path, "w") as file:
            file.writelines(new_lines)

    def mutate_chrg(
        self, chrg_to_mutate: str, old_OS: int, new_OS: int, save_path: str
    ) -> None:
        """
        Mutate the charge file (.CHRG) with a new oxidation state and save it to a new location.

        Args:
            chrg_to_mutate (str): Path to the original .CHRG file that needs to be mutated.
            old_OS (int): The initial oxidation state in the old .CHRG file.
            new_OS (int): The new oxidation state to replace the old oxidation state.
            save_path (str): The path where the new mutated .CHRG file will be saved.

        Raises:
            IOError: If the file path provided does not end with .CHRG.
        """
        if not chrg_to_mutate.endswith(".CHRG"):
            raise IOError("This must be a path to .CHRG file!")

        initial_total_charge = 0

        # Read the original .CHRG file and get the initial total charge
        with open(chrg_to_mutate, "r") as file:
            all_lines = file.readlines()
            charge_parsed = int(all_lines[0].strip())
            initial_total_charge = charge_parsed

        # Calculate the charge of ligands based on the initial total charge and old oxidation state
        ligands_charge = initial_total_charge - old_OS

        # Calculate the new total charge based on ligands charge and new oxidation state
        new_total_charge = ligands_charge + new_OS
        assert isinstance(new_total_charge, int)

        save_chrg(new_total_charge, save_path)

    def calc_multiplicity(self, CA: str, OS: int) -> int:
        """
        Calculate the multiplicity value for a given central atom (CA) and oxidation state (OS).

        This function currently supports lanthanides and actinides, and oxidation states up to +6.

        Args:
            CA (str): The symbol of the central atom for which the multiplicity is to be calculated.
                The symbol should match one of the known lanthanides or actinides.
            OS (int): The oxidation state of the central atom. Must be an integer up to +6.

        Returns:
            int: The multiplicity value for the given CA and OS.

        Raises:
            ValueError: If the CA is not among lanthanides or actinides, or if the OS is greater than +6.
        """

        if OS > 6:
            raise ValueError("This function supports the oxidation states up to +6.")

        if CA.capitalize() in lanthanides:
            df = ln_multiplicity
        elif CA.capitalize() in actinides:
            df = ac_multiplicity
        else:
            raise ValueError(
                "This function works now only for lanthanides and actinides!"
            )

        return int(df[df["element"] == CA.lower()][str(OS)])

    def mutated_uid(self, uid: str, new_ca: str) -> str:
        """
        Generate a mutated UID based on the original UID, the new central atom (CA),
        and the new oxidation state.

        Args:
            uid (str): The original unique identifier (UID) for the sample.
            new_ca (str): The symbol of the new central atom to which the sample will be mutated.

        Returns:
            str: The mutated UID, formed by appending information about the mutation to the original UID.
        """
        return f"{uid}_mutated_{new_ca}_{self.oxidation_state_new}"
