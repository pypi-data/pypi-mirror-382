import pytest

from qcinf.utils import rotate_structure

pytest.importorskip("rdkit")  # tries `import rdkit` skips tests if not installed


from qcinf._backends.rdkit import (
    _rmsd_rdkit,
    _smiles_to_structure_rdkit,
    _structure_to_smiles_rdkit,
)


def test_rmsd_identity(water):
    assert _rmsd_rdkit(water, water) == pytest.approx(0.0, abs=1e-6)


def test_rmsd_alignment_happens_before_rmsd(water):
    water2 = rotate_structure(water, "z", 90.0)
    assert _rmsd_rdkit(water, water2, symmetry=False) == pytest.approx(0.0, abs=1e-6)


def test_smiles_to_structure():
    struct = _smiles_to_structure_rdkit("OCC", force_field="UFF")
    assert struct.symbols == ["O", "C", "C", "H", "H", "H", "H", "H", "H"]
    assert struct.charge == 0
    assert struct.multiplicity == 1
    assert struct.identifiers.smiles == "OCC"
    assert struct.identifiers.canonical_smiles == "CCO"


def test_smiles_to_structure_charges():
    # Check Charge
    struct = _smiles_to_structure_rdkit("[O-]CC")
    assert struct.charge == -1


def test_smiles_to_structure_multiplicity():
    # Check manual multiplicity
    struct = _smiles_to_structure_rdkit("[O-]CC", multiplicity=3)
    assert struct.charge == -1
    assert struct.multiplicity == 3


def test_smiles_charges_round_trip():
    """Test that SMILES with charges are handled correctly."""
    s = _smiles_to_structure_rdkit("CC[O-]")
    assert s.charge == -1
    # Using robust method
    assert _structure_to_smiles_rdkit(s) == "CC[O-]"


def test_structure_to_smiles_hydrogens(water):
    smiles = _structure_to_smiles_rdkit(water)
    assert smiles == "O"
    smiles = _structure_to_smiles_rdkit(water, hydrogens=True)
    assert smiles == "[H]O[H]"
