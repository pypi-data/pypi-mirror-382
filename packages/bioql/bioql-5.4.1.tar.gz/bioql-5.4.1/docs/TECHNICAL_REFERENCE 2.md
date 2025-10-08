# BioQL Technical Reference Guide
## Documentación Técnica Completa v2.0.0

### 🎯 **Visión General**
BioQL v2.0.0 es una plataforma de computación cuántica para bioinformática que integra procesamiento de lenguaje natural, representación intermedia (IR) y ejecución en backends cuánticos reales con autenticación API para monetización.

---

## 📋 **Tabla de Contenidos**
1. [Instalación y Setup](#instalación-y-setup)
2. [Autenticación API](#autenticación-api)
3. [Función Quantum Principal](#función-quantum-principal)
4. [DevKit Enhanced Features](#devkit-enhanced-features)
5. [CLI Commands](#cli-commands)
6. [Python API Reference](#python-api-reference)
7. [Natural Language Processing](#natural-language-processing)
8. [Quantum Backends](#quantum-backends)
9. [Molecular Docking](#molecular-docking)
10. [Sequence Alignment](#sequence-alignment)
11. [Advanced Features](#advanced-features)
12. [Examples & Use Cases](#examples--use-cases)

---

## 🚀 **Instalación y Setup**

### **Instalación desde PyPI**
```bash
# Instalación básica
pip install bioql

# Instalación completa con dependencias opcionales
pip install bioql[dev,cloud,visualization]

# Instalación desde fuente
git clone https://github.com/bioql/bioql.git
cd bioql
pip install -e .
```

### **Verificación de Instalación**
```bash
# CLI check
bioql check

# Python check
python -c "import bioql; print(bioql.get_version())"

# Test básico
bioql quantum "Create Bell state" --api-key YOUR_KEY --shots 10
```

### **Configuración de API Keys**
```bash
# Setup interactivo
bioql setup-keys

# Variable de entorno
export BIOQL_API_KEY="bioql_your_key_here"

# Archivo de configuración
echo 'BIOQL_API_KEY="bioql_your_key_here"' > ~/.bioql/.env
```

---

## 🔐 **Autenticación API**

### **Obtener API Key**
1. Registro: https://bioql.com/signup
2. Login: https://bioql.com/login
3. Dashboard → API Keys → Generate New

### **Planes Disponibles**
| Plan | Precio | Shots/Mes | Hardware Real | DevKit |
|------|--------|-----------|---------------|--------|
| **Free** | $0 | 1,000 | ❌ | ✅ |
| **Pro** | $29 | 50,000 | ✅ | ✅ |
| **Enterprise** | $299 | Ilimitado | ✅ | ✅ |

### **Autenticación en Código**
```python
import bioql

# Método 1: Parámetro directo
result = bioql.quantum("Create Bell state", api_key="bioql_your_key")

# Método 2: Variable de entorno
import os
os.environ['BIOQL_API_KEY'] = "bioql_your_key"
result = bioql.quantum("Create Bell state")

# Método 3: Archivo .env
from dotenv import load_dotenv
load_dotenv()
result = bioql.quantum("Create Bell state")
```

---

## ⚛️ **Función Quantum Principal**

### **quantum() - Función Clásica**
```python
bioql.quantum(
    program: str,                    # Código BioQL o descripción natural
    api_key: str,                   # API key requerida
    backend: str = 'simulator',     # Backend cuántico
    shots: int = 1024,              # Número de shots
    debug: bool = False,            # Modo debug
    token: Optional[str] = None,    # Token IBM Quantum
    instance: Optional[str] = None, # Instancia IBM
    timeout: int = 3600,           # Timeout en segundos
    auto_select: bool = False      # Auto-selección de backend
) -> QuantumResult
```

### **enhanced_quantum() - DevKit Function**
```python
bioql.enhanced_quantum(
    program: str,                    # Natural language o BioQL
    api_key: str,                   # API key requerida
    backend: str = 'simulator',     # Backend cuántico
    shots: int = 1024,              # Número de shots
    debug: bool = False,            # Modo debug
    token: Optional[str] = None,    # Token IBM Quantum
    instance: Optional[str] = None, # Instancia IBM
    timeout: int = 3600,           # Timeout en segundos
    auto_select: bool = False,     # Auto-selección de backend
    use_nlp: bool = True,          # 🆕 Procesamiento NL
    use_ir_compiler: bool = True,  # 🆕 Compilador IR
    return_ir: bool = False        # 🆕 Retornar IR
) -> Union[QuantumResult, Dict[str, Any]]
```

### **QuantumResult Structure**
```python
class QuantumResult:
    success: bool                    # Éxito de ejecución
    counts: Dict[str, int]          # Resultados cuánticos
    error_message: Optional[str]     # Mensaje de error
    total_shots: int                # Total de shots ejecutados
    most_likely_outcome: str        # Resultado más probable
    execution_time: float           # Tiempo de ejecución
    backend_name: str              # Backend usado
    job_id: Optional[str]          # ID del trabajo
    bio_interpretation: Dict       # 🆕 Interpretación biológica
    cost_estimate: float           # 🆕 Estimación de costo
    metadata: Dict[str, Any]       # 🆕 Metadatos enhanceados
```

---

## 🧠 **DevKit Enhanced Features**

### **Natural Language Processing**
```python
# Ejemplos de queries naturales soportadas
queries = [
    # Molecular Docking
    "Dock ligand SMILES 'CCO' to protein PDB 1ABC with 20 poses",
    "Dock drug aspirin to protein cyclooxygenase",
    "Bind molecule caffeine to adenosine receptor with energy threshold -8.0",

    # Sequence Alignment
    "Align DNA sequences ATCGATCG and ATCGATCGATCG",
    "Align protein sequences MKLLVL and MKLLVLCL with high similarity",
    "Find optimal alignment between sequences with 95% similarity",

    # Protein Folding
    "Fold protein sequence MKLLVLCL using quantum simulation",
    "Analyze protein hemoglobin folding stability",
    "Simulate 100 amino acid interactions",

    # Drug Discovery
    "Optimize drug-target interaction for compound X",
    "Calculate binding affinity between drug and protein",
    "Model hydrogen bonds using quantum states"
]

# Ejecución con enhanced_quantum
for query in queries:
    result = bioql.enhanced_quantum(
        program=query,
        api_key="your_key",
        use_nlp=True,
        use_ir_compiler=True,
        return_ir=True
    )

    if isinstance(result, dict):
        quantum_result = result['result']
        ir_program = result['ir']
        print(f"Domain: {ir_program.operations[0].domain.value}")
        print(f"Bio interpretation: {quantum_result.bio_interpretation}")
```

### **Intermediate Representation (IR)**
```python
from bioql.ir import BioQLProgram, DockingOperation, AlignmentOperation
from bioql.parser import NaturalLanguageParser

# Parsing natural language to IR
parser = NaturalLanguageParser()
program = parser.parse(
    "Dock ligand SMILES CCO to protein PDB 1ABC with 20 poses",
    "Docking Example"
)

print(f"Program: {program.name}")
print(f"Operations: {len(program.operations)}")
print(f"Domain: {program.operations[0].domain.value}")
print(f"Backend: {program.backend.value}")
```

### **Multi-Backend Compilation**
```python
from bioql.compilers import create_compiler
from bioql.ir import QuantumBackend

# Crear compilador específico
qiskit_compiler = create_compiler(QuantumBackend.QISKIT)
cirq_compiler = create_compiler(QuantumBackend.CIRQ)

# Compilar programa IR a circuito cuántico
compiled_circuit = qiskit_compiler.compile_program(program)
result = qiskit_compiler.execute(compiled_circuit, shots=1000)

print(f"Circuit depth: {result.results['circuit_depth']}")
print(f"Gate count: {result.results['gate_count']}")
print(f"Execution time: {result.execution_time}")
```

---

## 💻 **CLI Commands**

### **Comandos Principales**
```bash
# Help y versión
bioql --help
bioql --version
bioql version

# Verificación de instalación
bioql check

# Configuración de API keys
bioql setup-keys
```

### **Comando quantum - Ejecución Enhanced**
```bash
# Sintaxis básica
bioql quantum "PROGRAM" --api-key KEY [OPTIONS]

# Opciones disponibles
--api-key KEY           # API key (requerida)
--shots N              # Número de shots (default: 1024)
--backend BACKEND      # Backend cuántico (default: simulator)
--enhanced             # Usar DevKit capabilities (default: True)
--no-enhanced          # Deshabilitar DevKit
--return-ir            # Retornar representación intermedia

# Ejemplos prácticos
bioql quantum "Dock ligand SMILES CCO to protein PDB 1ABC" \
    --api-key bioql_your_key \
    --shots 500 \
    --backend qiskit \
    --return-ir

bioql quantum "Align DNA sequences ATCG and ATCGATCG" \
    --api-key bioql_your_key \
    --shots 100 \
    --backend simulator

bioql quantum "Create Bell state" \
    --api-key bioql_your_key \
    --no-enhanced \
    --backend ibm_brisbane
```

### **Comando compile - Compilación de Archivos**
```bash
# Compilar archivo BioQL
bioql compile file.bql

# Compilar con output específico
bioql compile input.bql --output compiled.qasm

# Ejemplo de archivo BioQL
cat > example.bql << EOF
# Docking molecular
dock ligand SMILES 'CCO' to protein PDB '1ABC'
set poses 20
set energy_threshold -6.0
execute with 1000 shots

# Análisis de secuencias
align sequences 'ATCGATCG' and 'ATCGATCGATCG'
set similarity 0.95
use quantum_fourier_transform
measure alignment_score
EOF

bioql compile example.bql
```

### **Comando example - Crear Ejemplos**
```bash
# Crear archivo de ejemplo
bioql example

# Crear con nombre específico
bioql example --name my_bioql_example.bql

# Contenido del ejemplo generado incluye:
# - Bell state creation
# - Protein folding analysis
# - DNA sequence alignment
# - Drug-protein binding simulation
# - Quantum circuits for biological processes
```

### **Comandos de Instalación IDE**
```bash
# Instalar extensión para Cursor IDE
bioql install cursor

# Instalar plugin para Windsurf IDE
bioql install windsurf
```

---

## 🐍 **Python API Reference**

### **Imports Principales**
```python
# Imports básicos
import bioql
from bioql import quantum, enhanced_quantum, QuantumResult

# Imports DevKit
from bioql.enhanced_quantum import enhanced_quantum
from bioql.ir import BioQLProgram, DockingOperation, AlignmentOperation
from bioql.parser import NaturalLanguageParser, LLMParser
from bioql.compilers import QiskitCompiler, CirqCompiler, create_compiler

# Imports utilitarios
from bioql.bio_interpreter import interpret_bio_results
from bioql.logger import get_logger, configure_logging
```

### **Configuración y Info**
```python
# Información del sistema
info = bioql.get_info()
print(f"Version: {info['version']}")
print(f"Qiskit available: {info['qiskit_available']}")
print(f"Python version: {info['python_version']}")

# Configurar debug mode
bioql.configure_debug_mode(True)

# Configurar logging
from bioql.logger import configure_logging
configure_logging(level="DEBUG")

# Verificar instalación
is_working = bioql.check_installation()
print(f"BioQL working: {is_working}")
```

### **Backends Disponibles**
```python
# Listar backends disponibles
backends = bioql.list_available_backends()
print("Available backends:", backends)

# Backends soportados:
BACKENDS = {
    'simulator': 'Local simulator',
    'aer': 'Qiskit Aer simulator',
    'qiskit': 'Qiskit local',
    'cirq': 'Cirq simulator',
    'ibm_brisbane': 'IBM Quantum Brisbane',
    'ibm_oslo': 'IBM Quantum Oslo',
    'ibm_eagle': 'IBM Eagle processor',
    'ionq_simulator': 'IonQ Simulator',
    'ionq_aria': 'IonQ Aria hardware'
}
```

---

## 🧬 **Natural Language Processing**

### **Dominios Soportados**
```python
from bioql.ir import BioQLDomain

SUPPORTED_DOMAINS = {
    BioQLDomain.DOCKING: "Molecular docking simulations",
    BioQLDomain.ALIGNMENT: "Sequence alignment algorithms",
    BioQLDomain.FOLDING: "Protein folding prediction",
    BioQLDomain.OPTIMIZATION: "Quantum optimization",
    BioQLDomain.GENERAL: "General quantum computing"
}
```

### **Keywords de Reconocimiento**
```python
# Docking keywords
DOCKING_KEYWORDS = [
    'dock', 'docking', 'bind', 'binding', 'ligand', 'protein',
    'receptor', 'poses', 'affinity', 'energy', 'interaction'
]

# Alignment keywords
ALIGNMENT_KEYWORDS = [
    'align', 'alignment', 'sequence', 'dna', 'rna', 'protein',
    'similarity', 'identity', 'gap', 'match', 'mismatch'
]

# Folding keywords
FOLDING_KEYWORDS = [
    'fold', 'folding', 'structure', 'conformation', 'stability',
    'energy', 'minimize', 'optimize', 'prediction'
]
```

### **Parser Configuration**
```python
from bioql.parser import NaturalLanguageParser

# Configurar parser
parser = NaturalLanguageParser()

# Parsing con configuración específica
program = parser.parse(
    text="Dock ligand SMILES 'CCO' to protein PDB 1ABC with 20 poses",
    program_name="Custom Docking",
    default_shots=2000,
    default_backend="qiskit"
)

# Parsing con LLM (requiere OpenAI/Anthropic API key)
from bioql.parser import LLMParser

llm_parser = LLMParser(
    provider="openai",  # or "anthropic"
    api_key="your_llm_api_key"
)

program = llm_parser.parse(
    "I want to simulate the interaction between caffeine and adenosine receptor",
    "Caffeine Docking Study"
)
```

---

## ⚛️ **Quantum Backends**

### **Simulator Backends**
```python
# Local simulators (gratuitos)
result = bioql.quantum(
    "Create Bell state",
    api_key="your_key",
    backend="simulator",  # Local simulator
    shots=1024
)

result = bioql.quantum(
    "Create superposition",
    api_key="your_key",
    backend="aer",  # Qiskit Aer simulator
    shots=1024
)
```

### **IBM Quantum Hardware**
```python
# Configurar token IBM
import os
os.environ['IBM_QUANTUM_TOKEN'] = "your_ibm_token"

# Ejecutar en hardware real
result = bioql.quantum(
    "Dock ligand to protein",
    api_key="your_key",
    backend="ibm_brisbane",  # Hardware cuántico real
    token="your_ibm_token",
    instance="ibm-q/open/main",
    shots=100  # Menor número para hardware real
)
```

### **IonQ Hardware**
```python
# Configurar token IonQ
os.environ['IONQ_API_KEY'] = "your_ionq_key"

# Ejecutar en IonQ
result = bioql.quantum(
    "Quantum optimization",
    api_key="your_key",
    backend="ionq_aria",  # IonQ Aria hardware
    shots=50
)
```

### **Auto-Selection de Backend**
```python
# Selección automática basada en programa
result = bioql.quantum(
    "Complex protein folding simulation",
    api_key="your_key",
    auto_select=True,  # BioQL elegirá el mejor backend
    shots=1000
)
```

---

## 🧪 **Molecular Docking**

### **Sintaxis de Docking**
```python
# Docking básico
result = bioql.enhanced_quantum(
    "Dock ligand SMILES 'CCO' to protein PDB 1ABC",
    api_key="your_key",
    shots=1000
)

# Docking con parámetros específicos
result = bioql.enhanced_quantum(
    "Dock ligand SMILES 'CCO' to protein PDB 1ABC with 50 poses and energy threshold -8.0",
    api_key="your_key",
    shots=2000,
    backend="qiskit"
)

# Docking de drug discovery
result = bioql.enhanced_quantum(
    "Dock drug aspirin to protein cyclooxygenase with binding analysis",
    api_key="your_key",
    shots=1500
)
```

### **Interpretación de Resultados**
```python
# Analizar resultados de docking
if result.success:
    bio_data = result.bio_interpretation

    print(f"Domain: {bio_data['bioql_domain']}")
    print(f"Operation: {bio_data['operation_type']}")

    if 'docking' in bio_data:
        docking_info = bio_data['docking']
        print(f"Receptor: {docking_info['receptor']}")
        print(f"Ligand: {docking_info['ligand']}")
        print(f"Expected poses: {docking_info['expected_poses']}")
        print(f"Energy threshold: {docking_info['energy_threshold']}")

    print(f"Quantum counts: {result.counts}")
    print(f"Most likely binding state: {result.most_likely_outcome}")
```

### **Formatos de Entrada Soportados**
```python
# SMILES strings
"Dock ligand SMILES 'CCO' to protein PDB 1ABC"
"Dock ligand SMILES 'C1=CC=CC=C1' to protein hemoglobin"

# Drug names
"Dock drug aspirin to protein cyclooxygenase"
"Dock drug caffeine to adenosine receptor"

# PDB IDs
"Dock ligand to protein PDB 1ABC"
"Dock compound X to protein PDB 2XYZ"

# Custom molecules
"Dock molecule ethanol to protein alcohol_dehydrogenase"
```

---

## 🧬 **Sequence Alignment**

### **Sintaxis de Alignment**
```python
# Alignment básico
result = bioql.enhanced_quantum(
    "Align DNA sequences ATCGATCG and ATCGATCGATCG",
    api_key="your_key",
    shots=1000
)

# Alignment con parámetros específicos
result = bioql.enhanced_quantum(
    "Align protein sequences MKLLVL and MKLLVLCL with similarity 95%",
    api_key="your_key",
    shots=1500
)

# Alignment múltiple
result = bioql.enhanced_quantum(
    "Align sequences ATCG, ATCGATCG, and ATCGATCGATCG with high similarity",
    api_key="your_key",
    shots=2000
)
```

### **Tipos de Secuencias**
```python
# DNA sequences
"Align DNA sequences ATCGATCG and TTCGATCG"
"Align genomic sequences with pattern matching"

# RNA sequences
"Align RNA sequences AUCGAUCG and UUCGAUCG"

# Protein sequences
"Align protein sequences MKLLVL and MKLLVLCL"
"Align amino acid sequences with gap penalties"

# Mixed alignment
"Align biological sequences using quantum fourier transform"
```

### **Algoritmos Cuánticos para Alignment**
```python
# Usar Quantum Fourier Transform
result = bioql.enhanced_quantum(
    "Align sequences ATCG and ATCGATCG using quantum fourier transform",
    api_key="your_key"
)

# Grover's algorithm para pattern matching
result = bioql.enhanced_quantum(
    "Find optimal alignment using grover algorithm",
    api_key="your_key"
)

# QAOA para optimization
result = bioql.enhanced_quantum(
    "Optimize sequence alignment using qaoa algorithm",
    api_key="your_key"
)
```

### **Análisis de Resultados**
```python
if result.success:
    bio_data = result.bio_interpretation

    if 'alignment' in bio_data:
        alignment_info = bio_data['alignment']
        print(f"Sequence count: {alignment_info['sequence_count']}")
        print(f"Sequences: {alignment_info['sequences']}")

    # Interpretar counts como alignment score
    total_counts = sum(result.counts.values())
    alignment_score = max(result.counts.values()) / total_counts
    print(f"Alignment confidence: {alignment_score:.2%}")
```

---

## 🔬 **Advanced Features**

### **Batch Processing**
```python
# Procesar múltiples queries
queries = [
    "Dock ligand SMILES 'CCO' to protein PDB 1ABC",
    "Align DNA sequences ATCG and ATCGATCG",
    "Fold protein sequence MKLLVL using quantum simulation"
]

results = []
for query in queries:
    result = bioql.enhanced_quantum(
        query,
        api_key="your_key",
        shots=500
    )
    results.append(result)

# Procesar resultados
for i, result in enumerate(results):
    print(f"Query {i+1}: {result.success}")
    if result.success:
        print(f"  Bio domain: {result.bio_interpretation.get('bioql_domain')}")
        print(f"  Cost: ${result.cost_estimate:.4f}")
```

### **Pipeline Customization**
```python
from bioql.parser import NaturalLanguageParser
from bioql.compilers import create_compiler
from bioql.ir import QuantumBackend

# Pipeline manual
parser = NaturalLanguageParser()
program = parser.parse(
    "Dock ligand SMILES 'CCO' to protein PDB 1ABC",
    "Custom Docking"
)

# Modificar programa IR
program.operations[0].num_poses = 100  # Más poses
program.operations[0].energy_threshold = -10.0  # Threshold estricto

# Compilar y ejecutar
compiler = create_compiler(QuantumBackend.QISKIT)
circuit = compiler.compile_program(program)
result = compiler.execute(circuit, shots=2000)
```

### **Monitoring y Logging**
```python
from bioql.logger import get_logger, configure_logging

# Configurar logging detallado
configure_logging(
    level="DEBUG",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = get_logger(__name__)

# Log personalizado
logger.info("Starting quantum docking simulation")

result = bioql.enhanced_quantum(
    "Dock ligand to protein",
    api_key="your_key",
    debug=True  # Habilitar debug logs
)

logger.info(f"Execution completed: {result.success}")
```

### **Cost Optimization**
```python
# Optimizar costos
def optimize_execution(query, api_key, max_cost=0.1):
    """Ejecutar con optimización de costo"""

    # Comenzar con shots bajos
    shots = 100

    while shots <= 2000:
        result = bioql.enhanced_quantum(
            query,
            api_key=api_key,
            shots=shots,
            backend="simulator"  # Usar simulator para estimar
        )

        if result.cost_estimate <= max_cost:
            # Ejecutar en hardware real si el costo es aceptable
            return bioql.enhanced_quantum(
                query,
                api_key=api_key,
                shots=shots,
                backend="ibm_brisbane"
            )

        shots += 100

    # Si no se puede ejecutar dentro del presupuesto
    return result

# Uso
result = optimize_execution(
    "Dock complex ligand to protein",
    "your_key",
    max_cost=0.05
)
```

### **Error Handling y Retry**
```python
import time
from typing import Optional

def robust_execution(
    query: str,
    api_key: str,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Optional[QuantumResult]:
    """Ejecución con retry automático"""

    for attempt in range(max_retries):
        try:
            result = bioql.enhanced_quantum(
                query,
                api_key=api_key,
                timeout=60  # Timeout corto
            )

            if result.success:
                return result
            else:
                print(f"Attempt {attempt + 1} failed: {result.error_message}")

        except Exception as e:
            print(f"Attempt {attempt + 1} error: {e}")

        if attempt < max_retries - 1:
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

    return None

# Uso
result = robust_execution(
    "Dock ligand to protein",
    "your_key",
    max_retries=5
)
```

---

## 📚 **Examples & Use Cases**

### **Drug Discovery Pipeline**
```python
def drug_discovery_pipeline(drug_smiles: str, target_protein: str, api_key: str):
    """Pipeline completo de drug discovery"""

    # 1. Docking inicial
    docking_result = bioql.enhanced_quantum(
        f"Dock ligand SMILES '{drug_smiles}' to protein {target_protein} with 50 poses",
        api_key=api_key,
        shots=1000
    )

    # 2. Análisis de binding affinity
    if docking_result.success:
        affinity_result = bioql.enhanced_quantum(
            f"Calculate binding affinity between {drug_smiles} and {target_protein}",
            api_key=api_key,
            shots=500
        )

        # 3. Optimización de interacción
        optimization_result = bioql.enhanced_quantum(
            f"Optimize drug-target interaction for {drug_smiles}",
            api_key=api_key,
            shots=800,
            backend="qiskit"
        )

        return {
            'docking': docking_result,
            'affinity': affinity_result,
            'optimization': optimization_result
        }

    return {'error': 'Docking failed'}

# Ejecutar pipeline
results = drug_discovery_pipeline(
    drug_smiles="CCO",  # Ethanol
    target_protein="alcohol_dehydrogenase",
    api_key="your_key"
)

print(f"Docking success: {results['docking'].success}")
print(f"Affinity analysis: {results['affinity'].bio_interpretation}")
```

### **Genomics Analysis**
```python
def genomics_analysis(sequences: list, api_key: str):
    """Análisis genómico completo"""

    results = {}

    # 1. Alignment múltiple
    seq_str = " and ".join([f"'{seq}'" for seq in sequences])

    alignment_result = bioql.enhanced_quantum(
        f"Align DNA sequences {seq_str} with high similarity",
        api_key=api_key,
        shots=1200
    )

    results['alignment'] = alignment_result

    # 2. Pattern matching con Grover
    if len(sequences) >= 2:
        pattern_result = bioql.enhanced_quantum(
            f"Find common patterns in sequences using grover algorithm",
            api_key=api_key,
            shots=800
        )
        results['patterns'] = pattern_result

    # 3. Análisis de variaciones
    variation_result = bioql.enhanced_quantum(
        f"Analyze genetic variations in sequences using quantum fourier transform",
        api_key=api_key,
        shots=600
    )
    results['variations'] = variation_result

    return results

# Ejecutar análisis
sequences = ["ATCGATCG", "ATCGATCGATCG", "TTCGATCG"]
genomics_results = genomics_analysis(sequences, "your_key")

for analysis_type, result in genomics_results.items():
    print(f"{analysis_type}: {result.success}")
    if result.success:
        print(f"  Domain: {result.bio_interpretation.get('bioql_domain')}")
        print(f"  Confidence: {max(result.counts.values()) / sum(result.counts.values()):.2%}")
```

### **Protein Engineering**
```python
def protein_engineering_workflow(
    original_sequence: str,
    target_properties: list,
    api_key: str
):
    """Workflow de ingeniería de proteínas"""

    results = {}

    # 1. Análisis de estructura original
    structure_result = bioql.enhanced_quantum(
        f"Analyze protein structure for sequence {original_sequence}",
        api_key=api_key,
        shots=1000
    )
    results['structure_analysis'] = structure_result

    # 2. Folding prediction
    folding_result = bioql.enhanced_quantum(
        f"Predict protein folding for sequence {original_sequence} using quantum simulation",
        api_key=api_key,
        shots=1500,
        backend="qiskit"
    )
    results['folding_prediction'] = folding_result

    # 3. Stability analysis
    stability_result = bioql.enhanced_quantum(
        f"Analyze protein stability and energy landscape for {original_sequence}",
        api_key=api_key,
        shots=800
    )
    results['stability'] = stability_result

    # 4. Optimization para target properties
    for prop in target_properties:
        opt_result = bioql.enhanced_quantum(
            f"Optimize protein sequence for {prop} using qaoa algorithm",
            api_key=api_key,
            shots=600
        )
        results[f'optimization_{prop}'] = opt_result

    return results

# Ejecutar workflow
protein_results = protein_engineering_workflow(
    original_sequence="MKLLVLCL",
    target_properties=["stability", "binding_affinity", "catalytic_activity"],
    api_key="your_key"
)

for step, result in protein_results.items():
    print(f"{step}: {result.success}")
    if result.success and hasattr(result, 'bio_interpretation'):
        print(f"  Bio data: {result.bio_interpretation}")
```

### **Comparative Analysis**
```python
def compare_algorithms(query: str, api_key: str, backends: list):
    """Comparar performance entre diferentes backends"""

    results = {}

    for backend in backends:
        try:
            result = bioql.enhanced_quantum(
                query,
                api_key=api_key,
                backend=backend,
                shots=500
            )

            results[backend] = {
                'success': result.success,
                'execution_time': result.execution_time,
                'cost': result.cost_estimate,
                'counts': result.counts,
                'bio_interpretation': result.bio_interpretation
            }

        except Exception as e:
            results[backend] = {'error': str(e)}

    return results

# Comparar backends
comparison = compare_algorithms(
    "Dock ligand SMILES 'CCO' to protein PDB 1ABC",
    "your_key",
    ["simulator", "aer", "qiskit", "cirq"]
)

print("Backend Comparison:")
for backend, data in comparison.items():
    if 'error' not in data:
        print(f"{backend}:")
        print(f"  Success: {data['success']}")
        print(f"  Time: {data['execution_time']:.2f}s")
        print(f"  Cost: ${data['cost']:.4f}")
    else:
        print(f"{backend}: Error - {data['error']}")
```

---

## 🔧 **Troubleshooting**

### **Errores Comunes**

#### **1. Authentication Error**
```python
# Error: Invalid API key
try:
    result = bioql.quantum("test", api_key="invalid_key")
except bioql.BioQLError as e:
    print(f"Auth error: {e}")
    print("Solution: Get valid API key from https://bioql.com/signup")
```

#### **2. Backend Not Available**
```python
# Error: Backend not available
try:
    result = bioql.quantum("test", api_key="key", backend="unknown_backend")
except bioql.QuantumBackendError as e:
    print(f"Backend error: {e}")
    print("Available backends:", bioql.list_available_backends())
```

#### **3. Rate Limiting**
```python
# Error: Rate limit exceeded
try:
    result = bioql.quantum("test", api_key="key")
except bioql.BioQLError as e:
    if "rate limit" in str(e).lower():
        print("Rate limited. Wait or upgrade plan.")
        print("Upgrade at: https://bioql.com/pricing")
```

#### **4. Parse Error**
```python
# Error: Natural language parsing failed
try:
    result = bioql.enhanced_quantum(
        "invalid query that cannot be parsed",
        api_key="key"
    )
except bioql.ProgramParsingError as e:
    print(f"Parse error: {e}")
    print("Try using more specific biological keywords")
```

### **Debug Mode**
```python
# Habilitar debug completo
bioql.configure_debug_mode(True)

result = bioql.enhanced_quantum(
    "Dock ligand to protein",
    api_key="your_key",
    debug=True  # Debug detallado
)

# Logs incluyen:
# - Natural language parsing steps
# - IR compilation details
# - Quantum circuit construction
# - Backend communication
# - Timing information
```

### **Performance Tuning**
```python
# Optimizar performance
result = bioql.enhanced_quantum(
    "Complex docking simulation",
    api_key="your_key",
    shots=100,          # Comenzar con pocos shots
    timeout=30,         # Timeout corto
    backend="simulator" # Usar simulator para testing
)

# Escalar gradualmente
if result.success:
    production_result = bioql.enhanced_quantum(
        "Complex docking simulation",
        api_key="your_key",
        shots=2000,         # Más shots para producción
        backend="qiskit",   # Backend más potente
        timeout=300         # Timeout mayor
    )
```

---

## 🔗 **Links y Recursos**

### **URLs Oficiales**
- **PyPI Package**: https://pypi.org/project/bioql/2.0.0/
- **Website**: https://bioql.com
- **Documentation**: https://docs.bioql.com
- **GitHub**: https://github.com/bioql/bioql
- **Support**: hello@spectrixrd.com

### **API Endpoints**
- **Authentication**: https://api.bioql.com/auth/validate
- **Billing**: https://api.bioql.com/billing/check-limits
- **Usage Tracking**: https://api.bioql.com/billing/record-usage

### **Third-party Integrations**
- **IBM Quantum**: https://quantum-computing.ibm.com/
- **IonQ**: https://cloud.ionq.com/
- **Qiskit**: https://qiskit.org/
- **Cirq**: https://quantumai.google/cirq

---

**© 2024 SpectrixRD - BioQL Technical Reference**
*Documentación completa para BioQL v2.0.0 con DevKit capabilities*
*Última actualización: $(date)*