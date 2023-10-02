import hashlib

from .ligand import Ligand


class Complex:
    def __init__(
        self, central_atom: str, central_atom_OS: int, central_atom_spin: int, CN: int
    ):
        """Compound structure created from central atom and ligands.

        Args:
            central_atom (str): Central atom's symbol.
            central_atom_OS (int): Central atom's oxidation state.
            central_atom_spin (int): Central atom's spin multiplicity (2S+1).
            CN (int): Coordination number of the complex.
        """

        self.central_atom = central_atom
        self.central_atom_OS = central_atom_OS
        self.central_atom_spin = central_atom_spin
        self.CN = CN
        self.remaining_sites = CN
        self.ligands_smiles = []
        self.ligands_coordLists = []
        self.ligands_keys = []
        self.ligands_types = []
        self.complex_ready = False
        self.complex_uid = None

    def add_ligand(self, ligand_dict: dict, ligand_key: str):
        """Add ligand to the complex.

        Args:
            ligand_dict (dict): Ligand's dictionary containing SMILES, coordList, and ligType. Element of ligands.json.
            ligand_key (str): Unique id of the ligand, keys in ligands.json.
        """

        ligand = Ligand(**ligand_dict)

        if ligand.denticity > self.remaining_sites:
            raise ValueError(
                "The denticity of ligand exceeds the number of remaining coordination sites!"
            )

        if self.complex_ready == True:
            raise ValueError(
                "The complex is already created, you cannot add more ligands!"
            )

        self.remaining_sites = self.remaining_sites - ligand.denticity
        self.ligands_smiles.append(ligand.smiles)
        self.ligands_coordLists.append(ligand.coordList)
        self.ligands_types.append(ligand.ligType)
        self.ligands_keys.append(ligand_key)

        if self.remaining_sites == 0:
            self.complex_ready = True
            self.complex_uid = self.get_uid()

    def get_inputDict(self) -> dict:
        """Summarizes all the necessary information for Architector's function build_complex() about complex and outputs it in
        appropriate dictionary formmat.

        Returns:
            dict : Input dictionary for Architector's function build_complex().
        """

        inputDict = {}

        # Initialize Core Dictionary
        coreDict = {}

        # Specify the metal:
        coreDict["metal"] = self.central_atom

        # Specify the coordination number (CN):
        coreDict["coreCN"] = self.CN

        # Add the core to the input dictionary:
        inputDict["core"] = coreDict

        # Initilize Ligand List
        ligList = []

        # Loop over ligands' smiles and CoordLists and save them into the ligList
        for smiles, coordList, ligType in zip(
            self.ligands_smiles, self.ligands_coordLists, self.ligands_types
        ):
            ligDict = {"smiles": smiles, "coordList": coordList, "ligType": ligType}

            ligList.append(ligDict)

        inputDict["ligands"] = ligList

        return inputDict

    def set_atom_parameters(
        self, inputDict: dict, metal_ox: int, full_spin: int
    ) -> dict:
        """Set atom parameters (central atom oxidation state and full spin of the compound).

        Args:
            inputDict (dict): Input dictionary for Architector's function build_complex().
            metal_ox (int): Central atom's oxidation state.
            full_spin (int): Full spin of the compound (2S + 1, where S is sum of the spin values of all electrons).

        Returns:
            dict: Input dictionary for Architector's function build_complex().
        """
        inputDict["parameters"] = {
            "metal_ox": metal_ox,
            "full_spin": full_spin,
        }
        return inputDict

    def get_uid(self) -> str:
        """Get unique hash (unique identifier) for the complex defined by central atom (CA),
        coordination number (CN), central atom oxidation state (OS), and list of ligand keys.

        Returns:
            str: Unique hash of the complex.
        """
        sorted_strings = sorted(self.ligands_keys)
        concatenated_strings = "_".join(sorted_strings)
        unique_string = f"{self.central_atom}_{self.CN}_{self.central_atom_OS}_{concatenated_strings}"
        unique_id = hashlib.md5(unique_string.encode()).hexdigest()
        return unique_id

    def get_remaining_coord_site_number(self) -> int:
        """Get the number of free (unoccupied) coordination sites of the complex.

        Returns:
            int: Number of unoccupied coordination sites.
        """
        return self.remaining_sites
