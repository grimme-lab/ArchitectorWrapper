# ArchitectorWrapper

<img src="logo.png" width="400">

Welcome to ArchitectorWrapper, a Python package designed to provide a convenient wrapper for the Architector package, which automates the generation of metal complexes.

## Introduction

ArchitectorWrapper is a user-friendly tool that simplifies the usage of the Architector package. With Architector, you can easily generate complex lanthanide or actinide structures with minimal effort, whether you're working on research projects, educational materials, or exploring the world of metal complexes.

For the Architector package see here:

1. Manuscript: Taylor, M.G., Burrill, D.J., Janssen, J., Batsita, E.R., Perez, D., and Yang. P. Architector for high-throughput cross-periodic table 3D complex building. Nat Commun 14, 2786 (2023). https://doi.org/10.1038/s41467-023-38169-2

2. Code: https://www.github.com/lanl/Architector 

## Installation

You can install ArchitectorWrapper using pip:

```bash
pip install git+https://github.com/grimme-lab/ArchitectorWrapper.git
```

## Features

This project mainly has three functionalities:

1. **Generation**: Generate a JSON file containing mono-compounds in string representation.
2. **Optimisation**: Create 3D representation of compounds and optimize those using the `Architector` package.
3. **Mutation**: For data augmentation, mutate the central atom through all lanthanides / actinides.



### Quickstart

Here is how to use the `generation` and `optimisation` functionalities.

#### Generation

Generate a dataset with 3 samples and `La` as central atom.

```python
from src import SampleDataset

# Generate the dataset with the specified parameters
dataset = SampleDataset.generate(
    central_atom="La",
    central_atom_OS=3,
    central_atom_spin=0,
    n_complexes=3,
    min_CN=5,
    max_CN=9,
)
```

#### Optimisation

Create 3D structures from a given `SampleDataset`. These structures are optimised geometries, as defined in the `settings`, hence the name "optimisation".

```python
from src import SampleDataset
from src import Optimiser

# Load samples from disk
dataset = SampleDataset.read(...)

# Define settings for Arcitector.build_complex()
settings = {
    "full_method": "GFN2-xTB",
    ...
}

# Run optimisation
opt = Optimiser(..., settings)
opt.run(dataset)
```

#### Mutation

Create permutations of lanthanides / actinides of given structures.

```python
from src import Mutator

# Original and new oxidation states are manually required
os = 3
os_new = 3

# Calculate mutations
mut = Mutator(dir, os, os_new)
mut.mutate()
```

For more details and usage examples, check out the `examples/` folder.
## Contributions and Issues

If you encounter any issues or have suggestions for improvements, please feel free to [open an issue](https://github.com/grimme-lab/ArchitectorWrapper/issues/new). We welcome contributions from the community and encourage you to submit pull requests.

## License

This project is licensed under the BSD 3-Clause License License - see the [LICENSE](LICENSE) file for details.

---

*Disclaimer: ArchitectorWrapper is not affiliated with the Architector package. ArchitectorWrapper provides a wrapper to simplify the usage of the Architector package for automatic generation of metal complexes.*
