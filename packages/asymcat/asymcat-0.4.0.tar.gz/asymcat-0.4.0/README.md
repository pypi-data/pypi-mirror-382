# ASymCat: Asymmetric Categorical Association Analysis

[![PyPI version](https://badge.fury.io/py/asymcat.svg)](https://badge.fury.io/py/asymcat)
[![Python versions](https://img.shields.io/pypi/pyversions/asymcat.svg)](https://pypi.org/project/asymcat/)
[![Code Quality](https://github.com/tresoldi/asymcat/workflows/Code%20Quality/badge.svg)](https://github.com/tresoldi/asymcat/actions)
[![codecov](https://codecov.io/gh/tresoldi/asymcat/branch/master/graph/badge.svg)](https://codecov.io/gh/tresoldi/asymcat)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ASymCat is a comprehensive Python library for analyzing **asymmetric associations** between categorical variables. Unlike traditional symmetric measures that treat relationships as bidirectional, ASymCat provides directional measures that reveal which variable predicts which, making it invaluable for understanding causal relationships, dependencies, and information flow in categorical data.

## Key Features

- **17+ Association Measures**: From basic MLE to advanced information-theoretic measures
- **Directional Analysis**: X→Y vs Y→X asymmetric relationship quantification
- **Robust Smoothing**: FreqProb integration for numerical stability
- **Multiple Data Formats**: Sequences, presence-absence matrices, n-grams
- **Scalable Architecture**: Optimized for large datasets with efficient algorithms

## Why Asymmetric Measures Matter

Traditional measures like Pearson's χ² or Cramér's V treat associations as symmetric: the relationship between X and Y is the same as between Y and X. However, many real-world relationships are inherently directional:

- **Linguistics**: Phoneme transitions may be predictable in one direction but not the other
- **Ecology**: Species presence may predict other species asymmetrically  
- **Market Research**: Product purchases may show directional dependencies
- **Medical Analysis**: Symptoms may predict conditions more reliably than vice versa

ASymCat quantifies these directional relationships, revealing hidden patterns that symmetric measures miss.

## Quick Example

```python
import asymcat

# Load your categorical data
data = asymcat.read_sequences("data.tsv")  # or read_pa_matrix() for binary data

# Collect co-occurrences  
cooccs = asymcat.collect_cooccs(data)

# Create scorer and analyze
scorer = asymcat.CatScorer(cooccs)

# Get asymmetric measures
mle_scores = scorer.mle()           # Maximum likelihood estimation
pmi_scores = scorer.pmi()           # Pointwise mutual information  
chi2_scores = scorer.chi2()         # Chi-square with smoothing
fisher_scores = scorer.fisher()     # Fisher exact test

# Each returns {(x, y): (x→y_score, y→x_score)}
print(f"A→B: {mle_scores[('A', 'B')][0]:.3f}")
print(f"B→A: {mle_scores[('A', 'B')][1]:.3f}")
```

## Installation

### From PyPI (Recommended)
```bash
pip install asymcat
```

### From Source
```bash
git clone https://github.com/tresoldi/asymcat.git
cd asymcat
pip install -e ".[dev]"  # Install with all optional dependencies
```

## Documentation & Resources

ASymCat provides comprehensive documentation organized for different needs:

### Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[User Guide](docs/USER_GUIDE.md)** | Conceptual foundations, theory, best practices | Everyone - start here |
| **[API Reference](docs/API_REFERENCE.md)** | Complete technical API documentation | Developers |
| **[LLM Documentation](docs/LLM_DOCUMENTATION.md)** | Quick integration and code patterns | AI agents, rapid development |

### Progressive Interactive Tutorials

Learn ASymCat through hands-on Nhandu tutorials with executable code and visualizations:

#### Tutorial 1: Basics
**Foundation** - Get started with asymmetric analysis
📄 [Python source](docs/tutorial_1_basics.py) | 🌐 [View HTML](https://htmlpreview.github.io/?https://github.com/tresoldi/asymcat/blob/master/docs/tutorial_1_basics.html)
- What are asymmetric associations and why they matter
- Basic workflow: load → collect → score
- Simple measures (MLE, PMI, Jaccard)
- Working with sequences and presence-absence data

#### Tutorial 2: Advanced Measures
**Depth** - Master all 17+ association measures
📄 [Python source](docs/tutorial_2_advanced_measures.py) | 🌐 [View HTML](https://htmlpreview.github.io/?https://github.com/tresoldi/asymcat/blob/master/docs/tutorial_2_advanced_measures.html)
- Information-theoretic measures (PMI, NPMI, Theil's U)
- Statistical measures (Chi-square, Cramér's V, Fisher)
- Smoothing methods and their effects
- Measure selection decision tree

#### Tutorial 3: Visualization
**Communication** - Create publication-quality figures
📄 [Python source](docs/tutorial_3_visualization.py) | 🌐 [View HTML](https://htmlpreview.github.io/?https://github.com/tresoldi/asymcat/blob/master/docs/tutorial_3_visualization.html)
- Heatmap visualizations of association matrices
- Score distribution and asymmetry plots
- Matrix transformations (scaling, inversion)
- Multi-measure comparison panels

#### Tutorial 4: Real-World Applications
**Application** - Complete analysis workflows
📄 [Python source](docs/tutorial_4_real_world.py) | 🌐 [View HTML](https://htmlpreview.github.io/?https://github.com/tresoldi/asymcat/blob/master/docs/tutorial_4_real_world.html)
- **Linguistics**: Grapheme-phoneme correspondence analysis
- **Ecology**: Galápagos finch species co-occurrence patterns
- **Machine Learning**: Feature selection with asymmetric measures
- Interpretation best practices and reporting strategies

> **All tutorials are fully executed with committed outputs** - view the HTML files online via the links above, or run the Python source files locally to explore and modify. Generate fresh documentation with `make docs`.

### Additional Resources
- **[Documentation Index](docs/README.md)**: Complete navigation guide
- **[CHANGELOG](CHANGELOG.md)**: Version history and migration guides


## Association Measures

ASymCat implements 17+ association measures organized by type:

### Probabilistic Measures
- **MLE**: Maximum Likelihood Estimation - P(X|Y) and P(Y|X)
- **Jaccard Index**: Set overlap with asymmetric interpretation

### Information-Theoretic Measures  
- **PMI**: Pointwise Mutual Information (log P(X,Y)/P(X)P(Y))
- **PMI Smoothed**: Numerically stable PMI with FreqProb smoothing
- **NPMI**: Normalized PMI [-1, 1] range
- **Mutual Information**: Average information shared
- **Conditional Entropy**: Information remaining after observing condition

### Statistical Measures
- **Chi-Square**: Pearson's χ² with optional smoothing
- **Cramér's V**: Normalized chi-square association
- **Fisher Exact**: Exact odds ratios for small samples
- **Log-Likelihood Ratio**: G² statistic

### Specialized Measures
- **Theil's U**: Uncertainty coefficient (entropy-based)
- **Tresoldi**: Custom measure designed for sequence alignment
- **Goodman-Kruskal λ**: Proportional reduction in error

## Data Formats

### Sequence Data (TSV)
```
# linguistic_data.tsv
sound_from	sound_to
p a t a	B A T A
k a t a	G A T A
```

### Presence-Absence Matrix (TSV)
```
# species_data.tsv
site	species_A	species_B	species_C
island_1	1	0	1
island_2	1	1	0
```

### N-gram Support
```python
# Automatic n-gram extraction
bigrams = asymcat.collect_cooccs(data, order=2, pad="#")
trigrams = asymcat.collect_cooccs(data, order=3, pad="#")
```

## Citation

The library is developed by Tiago Tresoldi (tiago.tresoldi@lingfil.uu.se). The library is developed in the context of the Cultural Evolution of Texts project, with funding from the [Riksbankens Jubileumsfond](https://www.rj.se/) (grant agreement ID: [MXM19-1087:1](https://www.rj.se/en/anslag/2019/cultural-evolution-of-texts/)).

During the first stages of development, the author received funding from the [European Research Council](https://erc.europa.eu/) (ERC) under the European Unionâ€™s Horizon 2020 research and innovation programme (grant agreement No. [ERC Grant #715618, Computer-Assisted Language Comparison](https://cordis.europa.eu/project/rcn/206320/factsheet/en)).

If you use ASymCat in your research, please cite:

```bibtex
@software{tresoldi_asymcat_2025,
  title = {ASymCat: Asymmetric Categorical Association Analysis},
  author = {Tresoldi, Tiago},
  address = {Uppsala},
  publisher = {Department of Linguistics and Philology, Uppsala University},
  year = {2025},
  url = {https://github.com/tresoldi/asymcat},
  version = {0.4.0}
}
```

## 🔮 Roadmap

- **Statistical Significance**: P-value calculations for all measures
- **Confidence Intervals**: Uncertainty quantification
- **GPU Acceleration**: CUDA support for massive datasets
- **Interactive Dashboards**: Web-based exploration tools
- **Extended Measures**: Additional domain-specific association metrics
- **Nhandu Documentation**: Migration to modern documentation system

