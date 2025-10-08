# BioQL - Quantum Computing for Bioinformatics & Drug Discovery

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-brightgreen.svg)](CHANGELOG.md)

**BioQL** is a revolutionary quantum computing framework specifically designed for bioinformatics and drug discovery applications. Combines natural language processing, quantum computing, and classical computational chemistry in a unified, easy-to-use package.

## ✨ What's New in v2.1.0 - Drug Discovery Pack

### 🧬 Complete Drug Discovery Toolkit
- **Molecular Docking**: AutoDock Vina + Quantum backends
- **Ligand Preparation**: SMILES → 3D with optimization
- **Receptor Preparation**: PDB cleaning and processing
- **Molecular Visualization**: PyMOL + py3Dmol integration
- **🔮 Dynamic Library Bridge**: Call ANY Python library via natural language!

[→ See Full Changelog](CHANGELOG.md) | [→ Quick Start Guide](docs/DRUG_DISCOVERY_QUICKSTART.md)

---

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install bioql

# With drug discovery features
pip install bioql[vina,viz]

# Complete installation
pip install bioql[vina,viz,openmm,dev]
```

### Example: Molecular Docking

```python
from bioql.docking import dock

# Dock aspirin to COX-2 enzyme
result = dock(
    receptor="cox2.pdb",
    ligand_smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
    backend="vina",
    output_dir="results/"
)

print(f"Binding score: {result.score:.2f} kcal/mol")
```

### Example: Dynamic Library Calls (🔮 Meta-wrapper)

Call **any** Python library using natural language:

```python
from bioql import dynamic_call

# Chemistry with RDKit
result = dynamic_call(
    "Use RDKit to calculate molecular weight of aspirin SMILES CC(=O)OC1=CC=CC=C1C(=O)O"
)
print(f"MW: {result.result} g/mol")

# Scientific computing with NumPy
result = dynamic_call(
    "Use numpy to calculate mean of array [1, 2, 3, 4, 5]"
)
print(f"Mean: {result.result}")

# Data analysis with Pandas
result = dynamic_call(
    "Use pandas to read CSV file data.csv and show first 5 rows"
)
print(result.result)
```

### Example: Quantum Computing

```python
from bioql import quantum

# Natural language quantum programming
result = quantum(
    "Create a Bell state with 2 qubits",
    api_key="YOUR_KEY",
    shots=1024
)

print(f"Results: {result.counts}")
```

---

## 🎯 Key Features

### Molecular Docking System
- **Multiple backends**: AutoDock Vina (classical) + Quantum computing
- **Auto backend selection**: Intelligent fallback system
- **SMILES input**: Direct from chemical notation
- **Configurable search**: Custom binding site and box size

### Chemistry Tools (`bioql.chem`)
- **Ligand prep**: SMILES → 3D with geometry optimization
- **Receptor prep**: PDB cleaning, water removal, chain selection
- **Format conversion**: PDB, PDBQT, MOL2, SDF
- **Multiple engines**: RDKit, OpenBabel, Meeko

### Visualization (`bioql.visualize`)
- **PyMOL integration**: Publication-quality rendering
- **Web fallback**: py3Dmol for Jupyter notebooks
- **Complex rendering**: Protein-ligand binding site visualization
- **Export options**: PNG, TIFF with ray tracing, PyMOL sessions

### 🔮 Dynamic Library Bridge (Meta-wrapper)
**Revolutionary feature**: Call any Python library via natural language!

- **Pre-configured libraries**: RDKit, NumPy, SciPy, Pandas, Biopython, PyMOL
- **Automatic parsing**: Extracts arguments from natural language
- **Extensible**: Register your own libraries
- **Code generation**: Shows executed code for learning

### Quantum Computing
- **Natural language interface**: Program quantum computers in plain English
- **DevKit pipeline**: NL → IR → Quantum execution
- **Multiple backends**: Qiskit, IBM Quantum, IonQ
- **Bioinformatics focus**: Specialized for biological applications

---

## 📚 Documentation

- **[Quick Start Guide](docs/DRUG_DISCOVERY_QUICKSTART.md)** - Get started in 5 minutes
- **[Technical Reference](TECHNICAL_REFERENCE.md)** - Complete API documentation
- **[Examples](examples/)** - Comprehensive usage examples
- **[Changelog](CHANGELOG.md)** - Version history and updates

---

## 💻 CLI Usage

### Molecular Docking
```bash
# Using AutoDock Vina
bioql dock \
  --receptor protein.pdb \
  --smiles "CC(=O)OC1=CC=CC=C1C(=O)O" \
  --backend vina

# Using Quantum Backend
bioql dock \
  --receptor protein.pdb \
  --smiles "CCO" \
  --backend quantum \
  --api-key YOUR_KEY
```

### Visualization
```bash
# Visualize structure
bioql visualize \
  --structure complex.pdb \
  --output image.png

# Visualize protein-ligand complex
bioql visualize \
  --structure protein.pdb \
  --ligand ligand.mol2 \
  --output binding_site.png
```

### Dynamic Library Calls
```bash
# Chemistry
bioql call "Use RDKit to calculate molecular weight of SMILES CCO"

# Scientific computing
bioql call "Use numpy to calculate mean of array [1, 2, 3, 4, 5]"

# Data analysis
bioql call "Use pandas to read CSV file data.csv and show first 5 rows"
```

### Quantum Computing
```bash
bioql quantum "Create Bell state" --api-key YOUR_KEY
bioql quantum "Simulate protein folding" --api-key YOUR_KEY --shots 1024
```

---

## 🔧 Configuration

### API Keys (for Quantum Backend)

```bash
# Environment variable
export BIOQL_API_KEY=your_key_here

# Or in code
from bioql import quantum
result = quantum("...", api_key="YOUR_KEY")
```

Get your API key at: **https://bioql.com/signup**

### External Tools

- **AutoDock Vina**: http://vina.scripps.edu/
- **PyMOL**: `conda install -c conda-forge pymol-open-source`

---

## 📦 Installation Extras

```bash
# Chemistry and docking
pip install bioql[vina]  # RDKit, Meeko, OpenBabel

# Visualization
pip install bioql[viz]  # py3Dmol, PIL

# Molecular dynamics
pip install bioql[openmm]  # OpenMM

# Development tools
pip install bioql[dev]  # pytest, black, mypy, etc.

# Everything
pip install bioql[vina,viz,openmm,dev]
```

---

## 🧪 Complete Workflow Example

```python
from bioql.chem import prepare_ligand, prepare_receptor
from bioql.docking import dock
from bioql.visualize import visualize_complex

# 1. Prepare receptor
receptor = prepare_receptor(
    "target.pdb",
    remove_waters=True,
    output_path="receptor_clean.pdb"
)

# 2. Prepare ligand from SMILES
ligand = prepare_ligand(
    "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
    output_path="ligand.pdb"
)

# 3. Perform docking
docking = dock(
    receptor=receptor.output_path,
    ligand_smiles="CC(=O)OC1=CC=CC=C1C(=O)O",
    backend="auto",  # Auto-select best backend
    output_dir="docking_results/"
)

# 4. Visualize results
viz = visualize_complex(
    receptor_path=receptor.output_path,
    ligand_path=ligand.output_path,
    output_image="binding_site.png"
)

print(f"✅ Workflow complete!")
print(f"   Binding score: {docking.score:.2f} kcal/mol")
print(f"   Visualization: {viz.output_path}")
```

---

## 🧬 Use Cases

- **Drug Discovery**: Virtual screening, lead optimization
- **Protein Engineering**: Structure analysis, binding site prediction
- **Quantum Chemistry**: Energy calculations, molecular properties
- **Bioinformatics**: Sequence analysis, structure prediction
- **Research**: Quantum algorithm development for biology

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Development setup
git clone https://github.com/bioql/bioql.git
cd bioql
pip install -e .[dev]
pytest
```

---

## 📊 Testing

```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/test_chem.py
pytest tests/test_docking.py
pytest tests/test_dynamic_bridge.py

# Run with coverage
pytest --cov=bioql --cov-report=html

# Skip slow/integration tests
pytest -m "not slow and not integration"
```

---

## 🐛 Troubleshooting

### "Vina executable not found"
Download AutoDock Vina from http://vina.scripps.edu/ and add to PATH.

### "PyMOL not available"
```bash
pip install bioql[viz]
# or
conda install -c conda-forge pymol-open-source
```

### "RDKit/Meeko required"
```bash
pip install bioql[vina]
```

### "API key required"
Get your free API key at https://bioql.com/signup

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qiskit** - IBM Quantum computing framework
- **RDKit** - Open-source cheminformatics
- **AutoDock Vina** - Molecular docking program
- **PyMOL** - Molecular visualization
- **Biopython** - Bioinformatics tools

---

## 📞 Support & Community

- **Issues**: https://github.com/bioql/bioql/issues
- **Discussions**: https://github.com/bioql/bioql/discussions
- **Email**: support@bioql.com
- **Documentation**: https://docs.bioql.com

---

## 🌟 Star History

If BioQL helps your research, please give us a ⭐️ on GitHub!

---

**Built with ❤️ by the BioQL Development Team**

© 2024-2025 BioQL. All rights reserved.