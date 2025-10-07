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

### Pedigree Generation:

**'pedigree_generator(FamilyID, max_children, mode, generation_count, SpouseLikelihood = 0.6, AffectedSpouse = True, BackpropLikelihood = 0.25, alt_freq = 0.1)'** - returns a dataframe with familial relation, sex, and phenotype information for individuals in the generated pedigree.

#### **Parameters**
- **FamilyID**(string): the ID name to be attached to the generated family pedigree
- **max_children**(int): the maximum number of children that should be generated for any reproductive pair within the pedigree
- **mode**['AD','AR']: the mode of inheritence to be used in generating the pedigree based on mendelian inheritance patters (AR= Autosomal Recessive, AD= Austosmal Dominant)
- **generation_count**(int): the number of generations to be represented in the generated pedigree
- **SpouseLikelihood**(float[0-1]): the likelihood that a reproductive partner will be generated for any offspring entry made over the course of pedigree forward propigation (default: 0.6)
- **AffectedSpouse**(bool): determines if any ofthe generated reproductive partners have a non-zero chance of being carriers of the alternate allele (default: true)
- **BackpropLikelihood**(float[0-1]): the likelihood that a parental history will be generated for any generated reproductive partner over the course of reverse pedigree propigation (default: 0.1)

### Additional Functionality:
**gen_PED_export(df, output_dir='.')**: exports the generated family pedigree as a formatted PED file named after assigned FamilyID found in dataframe (i.e. 'FamilyID'.ped). 
- df(DataFame): generated family pedigree dataframe object
- output_dir(string): destination directory for exported PED file, default is working directory

**plot_pedigree_tree(df, title="Pedigree (Tree Layout)")**: displays directed graphical representation of the generated pedigree. 
- df(DataFame): generated family pedigree dataframe object
- title(string): title to be displayed with pedigree graph

**construct_pedigree_graph(df)**: contructs a networkx.DiGraph object representing the given pedigree dataframe to be used in further graphical analysis of pedigrees


## License

[MIT]
(https://choosealicense.com/licenses/mit/)