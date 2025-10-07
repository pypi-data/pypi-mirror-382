# __init__.py for the ASymCat library

"""
ASymCat: a library for symmetric and asymmetric analysis of categorical co-occurrences

ASymCat is a Python library for obtaining symmetric and asymmetric measures of association between categorical
variables in data exploration and description.
"""

# Information on the package
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"
__version__ = "0.4.0"

# Build the namespace
from asymcat import correlation, scorer
from asymcat.common import (
    build_ct,
    collect_alphabets,
    collect_cooccs,
    collect_ngrams,
    collect_observations,
    read_pa_matrix,
    read_sequences,
)

__all__ = [
    "build_ct",
    "collect_alphabets",
    "collect_cooccs",
    "collect_ngrams",
    "collect_observations",
    "correlation",
    "read_pa_matrix",
    "read_sequences",
    "scorer",
]
