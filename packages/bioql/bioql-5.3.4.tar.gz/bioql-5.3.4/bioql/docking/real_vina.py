"""
BioQL Real Molecular Docking with AutoDock Vina - v5.3.0

Docking REAL usando AutoDock Vina (no simulado, no interpretado).
Resultados auditables y reproducibles.

Requisitos:
  pip install rdkit meeko vina
  O tener vina en PATH como binario
"""

import os
import shutil
import math
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    HAVE_RDKIT = True
except ImportError:
    HAVE_RDKIT = False

try:
    from meeko import MoleculePreparation, PDBQTMolecule
    HAVE_MEEKO = True
except ImportError:
    HAVE_MEEKO = False

# Buscar binario de Vina
VINA_BIN = shutil.which("vina")


@dataclass
class VinaPose:
    """Una pose de docking con su energía."""
    rank: int
    affinity_kcal_per_mol: float
    rmsd_lb: float
    rmsd_ub: float


@dataclass
class VinaResult:
    """Resultado completo de docking con Vina."""
    ligand_smiles: str
    receptor_pdb: str
    best_affinity: float
    poses: List[VinaPose]
    num_poses: int
    runtime_seconds: float
    output_pdbqt: str
    log_file: str
    center: Tuple[float, float, float]
    box_size: Tuple[float, float, float]
    timestamp: str

    def to_dict(self):
        return {
            "ligand_smiles": self.ligand_smiles,
            "receptor_pdb": self.receptor_pdb,
            "best_affinity_kcal_per_mol": self.best_affinity,
            "num_poses": self.num_poses,
            "poses": [{"rank": p.rank, "affinity": p.affinity_kcal_per_mol,
                      "rmsd_lb": p.rmsd_lb, "rmsd_ub": p.rmsd_ub}
                     for p in self.poses],
            "runtime_seconds": self.runtime_seconds,
            "output_pdbqt": self.output_pdbqt,
            "log_file": self.log_file,
            "center": self.center,
            "box_size": self.box_size,
            "timestamp": self.timestamp
        }

    def calculate_ki(self, temp_K: float = 298.15) -> float:
        """Calcula Ki (nM) desde ΔG usando termodinámica."""
        R = 1.98720425864083e-3  # kcal/(mol·K)
        try:
            Ki_M = math.exp(self.best_affinity / (R * temp_K))
            return Ki_M * 1e9  # Convertir a nM
        except OverflowError:
            return float("inf")

    def calculate_ic50(self, temp_K: float = 298.15) -> float:
        """Calcula IC50 (nM) aproximado como ~2*Ki."""
        return self.calculate_ki(temp_K) * 2


def prepare_ligand_pdbqt(smiles: str, output_pdbqt: Path) -> None:
    """
    Prepara ligando desde SMILES a PDBQT usando RDKit + Meeko.

    Args:
        smiles: SMILES string del ligando
        output_pdbqt: Ruta de salida del PDBQT
    """
    if not HAVE_RDKIT:
        raise RuntimeError("RDKit no está instalado. pip install rdkit")
    if not HAVE_MEEKO:
        raise RuntimeError("Meeko no está instalado. pip install meeko")

    # Convertir SMILES a molécula 3D
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES inválido: {smiles}")

    # Añadir hidrógenos
    mol = Chem.AddHs(mol)

    # Generar conformación 3D
    params = AllChem.ETKDGv3()
    params.randomSeed = 42  # Reproducibilidad
    AllChem.EmbedMolecule(mol, params)

    # Optimizar geometría
    AllChem.UFFOptimizeMolecule(mol, maxIters=500)

    # Convertir a PDBQT con Meeko
    prep = MoleculePreparation()
    mol_setups = prep.prepare(mol)

    # Escribir PDBQT
    with open(output_pdbqt, 'w') as f:
        for setup in mol_setups:
            f.write(setup.write_pdbqt_string())


def prepare_receptor_pdbqt(pdb_path: Path, output_pdbqt: Path) -> None:
    """
    Prepara receptor desde PDB a PDBQT.

    Nota: Para producción, usa MGLTools prepare_receptor4.py:
      prepare_receptor4.py -r protein.pdb -o protein.pdbqt -A hydrogens

    Esta función asume que ya tienes un PDBQT preparado o usa conversión simple.
    """
    if pdb_path.suffix.lower() == ".pdbqt":
        # Ya está en formato PDBQT
        shutil.copy(pdb_path, output_pdbqt)
        return

    # Si es PDB, necesitas MGLTools o similar
    raise RuntimeError(
        f"Receptor debe estar en formato PDBQT. "
        f"Usa MGLTools para convertir: "
        f"prepare_receptor4.py -r {pdb_path} -o {output_pdbqt} -A hydrogens"
    )


def run_vina_docking(
    receptor_pdbqt: Path,
    ligand_pdbqt: Path,
    center: Tuple[float, float, float],
    box_size: Tuple[float, float, float],
    output_dir: Path,
    exhaustiveness: int = 8,
    num_modes: int = 9
) -> VinaResult:
    """
    Ejecuta docking con AutoDock Vina.

    Args:
        receptor_pdbqt: Ruta al receptor en formato PDBQT
        ligand_pdbqt: Ruta al ligando en formato PDBQT
        center: Centro de la caja de búsqueda (x, y, z) en Å
        box_size: Tamaño de la caja (sx, sy, sz) en Å
        output_dir: Directorio de salida
        exhaustiveness: Exhaustividad de búsqueda (default: 8)
        num_modes: Número máximo de modos de binding (default: 9)

    Returns:
        VinaResult con todas las poses y energías
    """
    if not VINA_BIN:
        raise RuntimeError(
            "AutoDock Vina no encontrado en PATH. "
            "Instala con: pip install vina "
            "O descarga de https://vina.scripps.edu/"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    out_pdbqt = output_dir / "vina_out.pdbqt"
    log_file = output_dir / "vina_log.txt"

    cx, cy, cz = center
    sx, sy, sz = box_size

    # Construir comando de Vina
    cmd = [
        VINA_BIN,
        "--receptor", str(receptor_pdbqt),
        "--ligand", str(ligand_pdbqt),
        "--center_x", str(cx),
        "--center_y", str(cy),
        "--center_z", str(cz),
        "--size_x", str(sx),
        "--size_y", str(sy),
        "--size_z", str(sz),
        "--exhaustiveness", str(exhaustiveness),
        "--num_modes", str(num_modes),
        "--out", str(out_pdbqt),
        "--log", str(log_file)
    ]

    # Ejecutar Vina
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Vina falló: {e.stderr}")

    runtime = time.time() - start_time

    # Parsear log para obtener resultados
    if not log_file.exists():
        raise RuntimeError("Vina no generó archivo de log")

    poses = parse_vina_log(log_file)

    if not poses:
        raise RuntimeError("No se encontraron poses en el log de Vina")

    best_affinity = poses[0].affinity_kcal_per_mol

    return VinaResult(
        ligand_smiles="",  # Se llena externamente
        receptor_pdb=str(receptor_pdbqt),
        best_affinity=best_affinity,
        poses=poses,
        num_poses=len(poses),
        runtime_seconds=runtime,
        output_pdbqt=str(out_pdbqt),
        log_file=str(log_file),
        center=center,
        box_size=box_size,
        timestamp=datetime.now().isoformat()
    )


def parse_vina_log(log_file: Path) -> List[VinaPose]:
    """
    Parsea el log de Vina para extraer poses y energías.

    Formato típico:
       mode |   affinity | dist from best mode
            | (kcal/mol) | rmsd l.b.| rmsd u.b.
    -----+------------+----------+----------
       1       -8.5      0.000      0.000
       2       -8.2      1.234      2.345
    """
    poses = []
    with open(log_file, 'r') as f:
        lines = f.readlines()

    parsing = False
    for line in lines:
        if "mode |" in line:
            parsing = True
            continue
        if parsing and "----" in line:
            continue
        if parsing:
            parts = line.strip().split()
            if len(parts) >= 4 and parts[0].isdigit():
                try:
                    rank = int(parts[0])
                    affinity = float(parts[1])
                    rmsd_lb = float(parts[2])
                    rmsd_ub = float(parts[3])

                    poses.append(VinaPose(
                        rank=rank,
                        affinity_kcal_per_mol=affinity,
                        rmsd_lb=rmsd_lb,
                        rmsd_ub=rmsd_ub
                    ))
                except (ValueError, IndexError):
                    continue

    return poses


def dock_smiles_to_receptor(
    smiles: str,
    receptor_pdbqt: Path,
    center: Tuple[float, float, float],
    box_size: Tuple[float, float, float],
    output_dir: Path,
    exhaustiveness: int = 8,
    num_modes: int = 9
) -> VinaResult:
    """
    Pipeline completo: SMILES → docking → resultados.

    Args:
        smiles: SMILES del ligando
        receptor_pdbqt: Receptor preparado en PDBQT
        center: Centro de la caja (x, y, z)
        box_size: Tamaño de la caja (sx, sy, sz)
        output_dir: Directorio de salida
        exhaustiveness: Exhaustividad de Vina
        num_modes: Número de modos

    Returns:
        VinaResult completo
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Preparar ligando
    ligand_pdbqt = output_dir / "ligand.pdbqt"
    prepare_ligand_pdbqt(smiles, ligand_pdbqt)

    # Ejecutar docking
    result = run_vina_docking(
        receptor_pdbqt=receptor_pdbqt,
        ligand_pdbqt=ligand_pdbqt,
        center=center,
        box_size=box_size,
        output_dir=output_dir,
        exhaustiveness=exhaustiveness,
        num_modes=num_modes
    )

    # Añadir SMILES al resultado
    result.ligand_smiles = smiles

    return result


__all__ = [
    'VinaPose',
    'VinaResult',
    'prepare_ligand_pdbqt',
    'prepare_receptor_pdbqt',
    'run_vina_docking',
    'dock_smiles_to_receptor',
    'HAVE_RDKIT',
    'HAVE_MEEKO',
    'VINA_BIN'
]
