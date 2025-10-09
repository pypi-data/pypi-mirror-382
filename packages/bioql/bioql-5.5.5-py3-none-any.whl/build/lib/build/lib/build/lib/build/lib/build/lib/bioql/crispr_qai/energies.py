"""
Quantum energy collapse estimation for gRNA-DNA interactions

Estimates binding affinity between guide RNA and target DNA using:
- Quantum Ising model
- Multiple backend support (simulator, Braket, Qiskit)
- Energy-based scoring
"""

from typing import Dict, List, Any, Optional
import numpy as np

from .featurization import encode_guide_sequence
from .adapters.base import QuantumEngine
from .adapters.simulator import LocalSimulatorEngine


def estimate_energy_collapse_simulator(
    guide_seq: str,
    coupling_strength: float = 1.0,
    shots: int = 1000,
    seed: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Estimate gRNA-DNA binding energy using local simulator

    Args:
        guide_seq: Guide RNA sequence (e.g., "ATCGAAGTC")
        coupling_strength: Base-pair coupling strength (default: 1.0)
        shots: Number of quantum measurements
        seed: Random seed for reproducibility
        metadata: Optional metadata (guide_id, target, etc.)

    Returns:
        {
            'energy_estimate': float,     # Estimated binding energy
            'confidence': float,          # Measurement confidence (0-1)
            'runtime_seconds': float,     # Execution time
            'backend': str,               # 'local_simulator'
            'guide_sequence': str,        # Original sequence
            'num_qubits': int,            # Circuit size
            'metadata': dict              # Original metadata
        }

    Example:
        >>> result = estimate_energy_collapse_simulator("ATCGAAGTC", shots=1000)
        >>> print(f"Energy: {result['energy_estimate']:.3f}")
        Energy: -2.456
    """
    # Encode sequence to angles
    angles = encode_guide_sequence(guide_seq)

    # Create simulator engine
    engine = LocalSimulatorEngine(shots=shots, seed=seed)

    # Run energy estimation
    result = engine.run_energy_estimation(
        angles=angles,
        coupling_strength=coupling_strength,
        metadata=metadata
    )

    # Add sequence info
    result['guide_sequence'] = guide_seq
    result['num_qubits'] = len(angles)

    return result


def estimate_energy_collapse_braket(
    guide_seq: str,
    backend_name: str = "SV1",
    coupling_strength: float = 1.0,
    shots: int = 1000,
    aws_region: str = "us-east-1",
    s3_bucket: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Estimate gRNA-DNA binding energy using AWS Braket

    Args:
        guide_seq: Guide RNA sequence
        backend_name: Braket device ('SV1', 'DM1', 'Aspen-M', 'Harmony')
        coupling_strength: Base-pair coupling strength
        shots: Number of measurements
        aws_region: AWS region
        s3_bucket: S3 bucket (required for hardware)
        metadata: Optional metadata

    Returns:
        Energy estimation results (same format as simulator)

    Example:
        >>> result = estimate_energy_collapse_braket(
        ...     "ATCGAAGTC",
        ...     backend_name="SV1",
        ...     shots=1000
        ... )
    """
    from .adapters.braket_adapter import BraketEngine

    # Encode sequence
    angles = encode_guide_sequence(guide_seq)

    # Create Braket engine
    engine = BraketEngine(
        backend_name=backend_name,
        shots=shots,
        aws_region=aws_region,
        s3_bucket=s3_bucket
    )

    # Validate backend
    if not engine.validate_backend():
        raise RuntimeError(f"Braket backend {backend_name} not available")

    # Run energy estimation
    result = engine.run_energy_estimation(
        angles=angles,
        coupling_strength=coupling_strength,
        metadata=metadata
    )

    # Add sequence info
    result['guide_sequence'] = guide_seq
    result['num_qubits'] = len(angles)

    return result


def estimate_energy_collapse_qiskit(
    guide_seq: str,
    backend_name: str = "aer_simulator",
    coupling_strength: float = 1.0,
    shots: int = 1000,
    ibm_token: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Estimate gRNA-DNA binding energy using IBM Qiskit

    Args:
        guide_seq: Guide RNA sequence
        backend_name: Qiskit backend ('aer_simulator', 'ibm_torino', etc.)
        coupling_strength: Base-pair coupling strength
        shots: Number of measurements
        ibm_token: IBM Quantum token (required for hardware)
        metadata: Optional metadata

    Returns:
        Energy estimation results (same format as simulator)

    Example:
        >>> result = estimate_energy_collapse_qiskit(
        ...     "ATCGAAGTC",
        ...     backend_name="aer_simulator",
        ...     shots=1000
        ... )
    """
    from .adapters.qiskit_adapter import QiskitEngine

    # Encode sequence
    angles = encode_guide_sequence(guide_seq)

    # Create Qiskit engine
    engine = QiskitEngine(
        backend_name=backend_name,
        shots=shots,
        ibm_token=ibm_token
    )

    # Validate backend
    if not engine.validate_backend():
        raise RuntimeError(f"Qiskit backend {backend_name} not available")

    # Run energy estimation
    result = engine.run_energy_estimation(
        angles=angles,
        coupling_strength=coupling_strength,
        metadata=metadata
    )

    # Add sequence info
    result['guide_sequence'] = guide_seq
    result['num_qubits'] = len(angles)

    return result


def estimate_energy_custom(
    guide_seq: str,
    engine: QuantumEngine,
    coupling_strength: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Estimate energy using custom quantum engine

    Args:
        guide_seq: Guide RNA sequence
        engine: Custom QuantumEngine instance
        coupling_strength: Base-pair coupling strength
        metadata: Optional metadata

    Returns:
        Energy estimation results

    Example:
        >>> from bioql.crispr_qai.adapters import LocalSimulatorEngine
        >>> engine = LocalSimulatorEngine(shots=5000, seed=42)
        >>> result = estimate_energy_custom("ATCGAAGTC", engine)
    """
    # Encode sequence
    angles = encode_guide_sequence(guide_seq)

    # Validate backend
    if not engine.validated and not engine.validate_backend():
        raise RuntimeError(f"Engine {engine.backend_name} not available")

    # Run energy estimation
    result = engine.run_energy_estimation(
        angles=angles,
        coupling_strength=coupling_strength,
        metadata=metadata
    )

    # Add sequence info
    result['guide_sequence'] = guide_seq
    result['num_qubits'] = len(angles)

    return result


def batch_energy_estimation(
    guide_sequences: List[str],
    engine: Optional[QuantumEngine] = None,
    coupling_strength: float = 1.0,
    shots: int = 1000
) -> List[Dict[str, Any]]:
    """
    Estimate energies for multiple guide sequences

    Args:
        guide_sequences: List of guide RNA sequences
        engine: Quantum engine (defaults to LocalSimulatorEngine)
        coupling_strength: Base-pair coupling strength
        shots: Number of measurements per guide

    Returns:
        List of energy estimation results

    Example:
        >>> guides = ["ATCGAAGTC", "GCTAGCTA", "TTAACCGG"]
        >>> results = batch_energy_estimation(guides, shots=1000)
        >>> for r in results:
        ...     print(f"{r['guide_sequence']}: {r['energy_estimate']:.3f}")
    """
    if engine is None:
        engine = LocalSimulatorEngine(shots=shots)

    results = []

    for guide_seq in guide_sequences:
        result = estimate_energy_custom(
            guide_seq=guide_seq,
            engine=engine,
            coupling_strength=coupling_strength
        )
        results.append(result)

    return results
