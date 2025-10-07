from ._version import version as __version__
from .core import pedigree_generator, construct_pedigree_graph, plot_pedigree_tree

#TODO integrate pedigree graph construction and pedigree ploting
__all__ = [
    "pedigree_generator",
    "construct_pedigree_graph",
    "plot_pedigree_tree",
]