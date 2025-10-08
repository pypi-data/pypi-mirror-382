# 🧬 BioQL Demo Credentials - Unlimited Simulator Access

## 🔑 Demo API Key (UNLIMITED IONQ SIMULATOR)

```
API Key: bioql_test_8a3f9d2c1e5b4f7a9c2d6e1f8b3a5c7d
Email: demo@bioql.com
Plan: Enterprise (Unlimited)
Backend: IonQ Simulator ONLY
Quota: UNLIMITED shots/month
Cost: $0.00
```

---

## 🚀 Quick Start (2 Minutes)

### 1. Install BioQL
```bash
pip install bioql
```

### 2. Run Demo Script
```bash
# Download and run the complete demo
python examples/demo_unlimited_simulator.py
```

### 3. Use in Your Own Code
```python
from bioql import quantum

# Your unlimited demo API key
API_KEY = "bioql_test_8a3f9d2c1e5b4f7a9c2d6e1f8b3a5c7d"

# 100% Natural Language Quantum Computing!
result = quantum(
    "create a bell state with two qubits and measure both",
    backend='ionq_simulator',
    api_key=API_KEY,
    shots=1000
)

print(result)
```

---

## 💻 Example: Drug Discovery in Natural Language

```python
from bioql import quantum

API_KEY = "bioql_test_8a3f9d2c1e5b4f7a9c2d6e1f8b3a5c7d"

# Simulate aspirin molecule
result = quantum(
    "simulate the molecular structure of aspirin using variational quantum eigensolver "
    "with 4 qubits to find ground state energy for drug optimization",
    backend='ionq_simulator',
    api_key=API_KEY,
    shots=2048
)
```

---

## 🧪 More Natural Language Examples

### Example 1: Quantum Search
```python
quantum(
    "apply grover search algorithm on 3 qubits to find target state 101",
    backend='ionq_simulator',
    api_key=API_KEY
)
```

### Example 2: Protein Folding
```python
quantum(
    "simulate small protein fragment folding using quantum annealing with 6 qubits",
    backend='ionq_simulator',
    api_key=API_KEY,
    shots=3000
)
```

### Example 3: Quantum Chemistry
```python
quantum(
    "calculate dipole moment and bond angles of water molecule H2O using 4 qubits",
    backend='ionq_simulator',
    api_key=API_KEY
)
```

### Example 4: Drug-Receptor Binding
```python
quantum(
    "compute binding energy between semaglutide and glp1 receptor "
    "using variational quantum eigensolver on 6 qubits",
    backend='ionq_simulator',
    api_key=API_KEY,
    shots=5000
)
```

### Example 5: Quantum Machine Learning
```python
quantum(
    "train quantum classifier on 4 qubits to predict drug toxicity "
    "using quantum neural network",
    backend='ionq_simulator',
    api_key=API_KEY
)
```

---

## 📊 What You Can Do with This Demo Key

✅ **UNLIMITED Simulations** on IonQ Simulator
✅ **NO COST** - Completely free for demos
✅ **100% Natural Language** - No quantum gates knowledge needed
✅ **All Algorithms**: VQE, QAOA, Grover, QFT, etc.
✅ **Drug Discovery** - Molecular simulations
✅ **Protein Folding** - Conformational analysis
✅ **Quantum ML** - Classification and regression
✅ **Up to 8 Qubits** - Complex circuits

---

## ⚠️ Restrictions

❌ **NO Real Quantum Hardware** - Simulator only
❌ **NO IBM Quantum** access
❌ **NO IonQ QPU** access
✅ **IonQ Simulator ONLY** - Perfect for learning and demos!

---

## 🎯 Complete Demo Script

The file `examples/demo_unlimited_simulator.py` includes 10 complete examples:

1. ✅ Bell State Creation
2. ✅ Aspirin Molecule Simulation (VQE)
3. ✅ Grover's Search Algorithm
4. ✅ Quantum Fourier Transform
5. ✅ Protein Folding Simulation
6. ✅ Water Molecule Bond Analysis
7. ✅ Quantum ML - Drug Toxicity Classifier
8. ✅ GHZ State (5-qubit entanglement)
9. ✅ QAOA Optimization
10. ✅ Semaglutide-GLP1R Binding Energy

**Run it:**
```bash
python examples/demo_unlimited_simulator.py
```

**Expected Output:**
```
======================================================================
🧬 BioQL Natural Language Quantum Computing Demo
======================================================================
✅ API Key: bioql_test_8...
✅ Backend: IonQ Simulator
✅ Quota: UNLIMITED
======================================================================

📌 Example 1: Create quantum entanglement (Bell State)
----------------------------------------------------------------------
✅ Completed!

📌 Example 2: Simulate aspirin molecule for drug discovery
----------------------------------------------------------------------
✅ Completed!

...

======================================================================
🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!
======================================================================

📊 Summary:
   • Total quantum circuits executed: 10
   • Total shots used: 27,360
   • Backend: IonQ Simulator
   • Cost: $0.00 (Unlimited Demo Access)
```

---

## 🌐 Alternative: Web Demo

If you prefer a web interface:

```bash
# Clone examples repository
git clone https://github.com/bioql/bioql-examples.git
cd bioql-examples

# Start demo server
python demo_server.py

# Open browser: http://localhost:8000
```

**Login:**
- Email: `demo@bioql.com`
- Password: `quantum2025`

---

## 📚 Documentation

- **Installation Guide:** https://docs.bioql.com/installation
- **Natural Language Syntax:** https://docs.bioql.com/nl-syntax
- **API Reference:** https://docs.bioql.com/api
- **Examples:** https://docs.bioql.com/examples

---

## 💰 Pricing (For Production Use)

This demo key is FREE and UNLIMITED for **simulator only**.

For production use with **real quantum hardware**:

| Plan | Price | IonQ QPU | IBM Quantum | Shots/Month |
|------|-------|----------|-------------|-------------|
| Free | $0 | ❌ | ❌ | 50 (simulator) |
| Academic | $49 | ❌ | ✅ | 500 |
| Biotech | $499 | ✅ | ✅ | 5,000 |
| Pharma | $4,999 | ✅ | ✅ | 999,999 |
| Enterprise | Custom | ✅ | ✅ | Unlimited |

**Get your production API key:** https://bioql.com/signup

---

## 🔧 Troubleshooting

### Issue: "Invalid API Key"
**Solution:** Make sure you're using the EXACT key:
```python
API_KEY = "bioql_test_8a3f9d2c1e5b4f7a9c2d6e1f8b3a5c7d"
```

### Issue: "Backend not available"
**Solution:** Use `ionq_simulator` (NOT `ionq_qpu`):
```python
backend='ionq_simulator'  # ✅ Correct
backend='ionq_qpu'        # ❌ Not allowed for demo
```

### Issue: Installation problems
**Solution:**
```bash
pip uninstall bioql -y
pip install bioql --upgrade
```

---

## 📞 Support

- **Email:** support@bioql.com
- **Discord:** https://discord.gg/bioql
- **GitHub Issues:** https://github.com/bioql/bioql/issues
- **Documentation:** https://docs.bioql.com

---

## ✨ Why BioQL?

### Before (Traditional Qiskit):
```python
from qiskit import QuantumCircuit, execute, Aer

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc)
```

### After (BioQL Natural Language):
```python
from bioql import quantum

result = quantum(
    "create a bell state with two qubits and measure both",
    backend='ionq_simulator',
    api_key=API_KEY
)
```

**164 BILLION natural language patterns** understand what you want! 🚀

---

## 🎬 Video Tutorials

1. **Quick Start (2 min):** https://youtu.be/bioql-quickstart
2. **Drug Discovery Demo (5 min):** https://youtu.be/bioql-drug-discovery
3. **Natural Language Guide (10 min):** https://youtu.be/bioql-nl-guide

---

## 📖 Citation

If you use BioQL in your research, please cite:

```bibtex
@software{bioql2025,
  title = {BioQL: Natural Language Quantum Computing for Bioinformatics},
  author = {BioQL Development Team},
  year = {2025},
  url = {https://bioql.com},
  version = {3.0.2}
}
```

---

## 🚀 Ready to Start?

```bash
# 1. Install
pip install bioql

# 2. Run demo
python -c "
from bioql import quantum

result = quantum(
    'create a bell state and measure both qubits',
    backend='ionq_simulator',
    api_key='bioql_test_8a3f9d2c1e5b4f7a9c2d6e1f8b3a5c7d'
)

print('🎉 BioQL is working! Results:', result)
"
```

**Welcome to the future of quantum computing!** 🧬⚛️
