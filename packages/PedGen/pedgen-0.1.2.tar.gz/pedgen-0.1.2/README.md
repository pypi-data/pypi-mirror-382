# Pedigree Generation Package

PedGen is a python package that can be used to generate genetically realistic pedigrees. Generated pedigrees can be visualized as directed acyclic graphs and exported in PED file format.

## Prerequisites

Some functionality included in PedGen relies on system-level dependencies, namely in instalation of Graphviz. Please ensure Graphviz is installed before using the pedigree visualization functionality:

**Unix**
```bash
sudo apt install graphviz libgraphviz-dev
```

**macOS(Homebrew)**
```bash
brew install graphviz
```

## Installation

All required Python dependencies will be installed automatically with this package using pip.
```bash
pip install PedGen
```

## Usage
The primary function included in this package, pedigree_generator, works to contruct a realistic pedigree based on mendelian inheritance patterns and alternate allele frequencies in accordance with Hardy-Weinberg equilibrium. The generated pedigree is represented as Pandas dataframe object followign PED file formatting.
**'pedigree_generator(FamilyID, max_children, mode, generation_count, SpouseLikelihood = 0.6, AffectedSpouse = True, backpropLikelihood = 0.25, alt_freq = 0.1)'** - returns a dataframe with familial relation, sex, and phenotype information for individuals in the generated pedigree.
**Parameters**

FamilyID (string): the ID to be assigned to the family



## License

[MIT]
(https://choosealicense.com/licenses/mit/)