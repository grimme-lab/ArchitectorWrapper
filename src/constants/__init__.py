import pandas as pd
from pathlib import Path

lanthanides = [
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
]
actinides = [
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
    "Fr",
    "Ra",
]

ln_multiplicity = pd.read_csv(
    Path(__file__).parent / "ln_multiplicities.csv", sep=";", index_col=0, dtype=str
)
ac_multiplicity = pd.read_csv(
    Path(__file__).parent / "ac_multiplicities.csv", sep=";", index_col=0, dtype=str
)
