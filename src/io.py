def save_xyz(mol: str, save_path: str) -> None:
    """Save the geometry in XYZ format.

    Args:
        mol (str): Molecular geometry in XYZ format that will be saved to some file.
        save_path (str): Path to save the XYZ geometry. Don't forget to include file extension!
    """
    mol.write_xyz(save_path)


def save_uhf(n_unpels: int, save_path: str) -> None:
    """Save number of unpaired electrons in .UHF file format.

    Args:
        n_unpels (int): Number of unpaired electrons to be saved.
        save_path (str): Path to save the number of unpaired electrons. Don't forget to include file extension!
    """
    with open(save_path, "w") as file:
        file.write(str(n_unpels))


def save_chrg(charge: int, save_path: str) -> None:
    """Save charge in .CHRG file format.

    Args:
        charge (int): Charge to be saved.
        save_path (str): Path to save the charge. Don't forget to include file extension!
    """
    with open(save_path, "w") as file:
        file.write(str(charge))
