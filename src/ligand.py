from pydantic import BaseModel
import numpy as np


class Ligand(BaseModel):
    """
    Represents a ligand with SMILES notation and coordination sites.

    Initialize via:

    ```python
    ligand = Ligand(**ligand_dict)
    ```
    """

    smiles: str
    """The SMILES notation for the ligand."""

    coordList: list[int]
    """List of atom numbers indicating coordination sites."""

    ligType: str
    """Ligand's type."""

    @property
    def denticity(self) -> int:
        """Get ligand's denticity.

        Returns:
            int: Ligand's denticity (total number of binding atoms).
        """
        return len(self.coordList)

    @staticmethod
    def get_random(ligands_dict: dict) -> "Ligand":
        """Get random ligand from dictionary containing multiple ligand options.

        Args:
            ligands_dict (dict): Dictionary containing multiple ligand dictionaries as values, and any unique keys.
            Example: ligands.json converted into python dict format.

        Returns:
            dict: Ligand's dictionary containing SMILES, coordList, and ligType.
        """
        keywords = list(ligands_dict.keys())
        total_ligands_number = len(keywords)
        random_index = np.random.randint(low=0, high=total_ligands_number)
        random_ligand_keyword = keywords[random_index]
        random_ligand_dict = ligands_dict[random_ligand_keyword]
        return random_ligand_dict, random_ligand_keyword
