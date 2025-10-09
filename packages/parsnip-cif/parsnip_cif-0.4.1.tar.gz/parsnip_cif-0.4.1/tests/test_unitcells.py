import re
import warnings
from contextlib import nullcontext
from importlib.util import find_spec

import numpy as np
import pytest
from ase import io
from ase.build import supercells
from conftest import (
    _arrstrip,
    _gemmi_read_keys,
    additional_data_array,
    all_files_mark,
    cif_files_mark,
)
from gemmi import cif
from more_itertools import flatten

from parsnip import CifFile
from parsnip._errors import ParseWarning


def _gemmi_read_table(filename, keys):
    try:
        return np.array(cif.read_file(filename).sole_block().find(keys))
    except (RuntimeError, ValueError):
        pytest.skip("Gemmi failed to read file!")


@all_files_mark
def test_read_symops(cif_data):
    parsnip_symops = cif_data.file.symops
    gemmi_symops = _gemmi_read_table(cif_data.filename, cif_data.file._symops_key)
    np.testing.assert_array_equal(parsnip_symops, gemmi_symops)


@all_files_mark  # TODO: test with conversions to numeric as well
def test_read_wyckoff_positions(cif_data):
    parsnip_data = cif_data.file.wyckoff_positions
    gemmi_data = _gemmi_read_table(cif_data.filename, cif_data.file._wyckoff_site_keys)
    gemmi_data = [[cif.as_number(val) for val in row] for row in gemmi_data]
    np.testing.assert_array_equal(parsnip_data, gemmi_data)


@all_files_mark
def test_read_cell_params(cif_data):
    parsnip_data = cif_data.file.read_cell_params()
    cell_keys = cif_data.file._cell_keys
    if cell_keys == []:
        np.testing.assert_equal(parsnip_data, np.full((6,), np.nan))
        return  # No cell keys found
    gemmi_data = _gemmi_read_keys(cif_data.filename, cell_keys)
    np.testing.assert_array_equal(parsnip_data, gemmi_data)

    normalized = cif_data.file.read_cell_params(normalize=True)
    assert normalized[3:] == parsnip_data[3:]  # Should not change the angles
    assert min(normalized[:3]) == 1


@cif_files_mark
def test_build_unit_cell_errors(cif_data):
    cif_data.file.__class__._SYMPY_AVAILABLE = False
    with pytest.raises(ImportError, match="Sympy is not available!"):
        cif_data.file.build_unit_cell(parse_mode="sympy")
    cif_data.file.__class__._SYMPY_AVAILABLE = find_spec("sympy") is not None
    with pytest.raises(ValueError, match="Parse mode 'asdf'"):
        cif_data.file.build_unit_cell(parse_mode="asdf")


@cif_files_mark
@pytest.mark.parametrize("n_decimal_places", [2, 3, 4, 5, 6, 9])
@pytest.mark.parametrize("parse_mode", ["python_float", "sympy"])
@pytest.mark.parametrize(
    "cols",
    [
        None,
        "_atom_site_type_symbol",
        ["_atom_site_type_symbol", "_atom_site_occupancy"],
    ],
)
def test_build_unit_cell(cif_data, n_decimal_places, parse_mode, cols):
    warnings.filterwarnings("ignore", "crystal system", category=UserWarning)

    if (
        "PDB_4INS_head.cif" in cif_data.filename
        or ("no42.cif" in cif_data.filename and n_decimal_places > 3)
        or ("COD_7228524" in cif_data.filename and n_decimal_places > 5)
    ):
        return

    should_raise = cols is not None and any(
        k not in flatten(cif_data.file.loop_labels) for k in np.atleast_1d(cols)
    )
    occupancies, read_data = None, None
    with (
        pytest.raises(ValueError, match=r"not included in the `_atom_site_fract_\[xyz")
        if should_raise
        else nullcontext()
    ):
        read_data = cif_data.file.build_unit_cell(
            n_decimal_places=n_decimal_places,
            additional_columns=cols,
            parse_mode=parse_mode,
        )

    if read_data is None:
        return  # ValueError was raised - exit the test

    if cols is None:
        parsnip_positions = read_data @ cif_data.file.lattice_vectors.T
    else:
        auxiliary_arr, parsnip_positions = read_data
        parsnip_positions = parsnip_positions @ cif_data.file.lattice_vectors.T

        che_symbols = _arrstrip(auxiliary_arr[:, 0], r"[^A-Za-z]+")
        if isinstance(cols, list):
            occupancies = _arrstrip(auxiliary_arr[:, 1], r"[^\d\.]+").astype(float)

    # Read the structure and extract to Python builtin types. Then, wrap into the box
    ase_file = io.read(cif_data.filename)
    ase_data = supercells.make_supercell(ase_file, np.diag([1, 1, 1]))

    # Arrays must be sorted to guarantee correct comparison
    parsnip_positions = np.array(
        sorted(parsnip_positions.round(14), key=lambda x: (x[0], x[1], x[2]))
    )
    ase_positions = np.array(
        sorted(ase_data.get_positions(), key=lambda x: (x[0], x[1], x[2]))
    )
    ase_symbols = np.array(ase_data.get_chemical_symbols())

    parsnip_minmax = [parsnip_positions.min(axis=0), parsnip_positions.max(axis=0)]
    ase_minmax = [ase_positions.min(axis=0), ase_positions.max(axis=0)]

    np.testing.assert_array_equal(parsnip_positions.shape, ase_positions.shape)
    np.testing.assert_allclose(parsnip_minmax, ase_minmax, atol=1e-12)

    if cols is not None:
        # NOTE: ASE saves the occupancies of the most dominant species!
        # Parsnip makes no assumptions regarding the correct occupancy
        # Check all if full occupancy, partial if occ is ndarray and None if occ is None
        mask = (
            ... if cif_data.file["_atom_site_occupancy"] is None else occupancies == 1
        )
        np.testing.assert_equal(che_symbols[mask], ase_symbols[mask])

    if "zeolite" in cif_data.filename or "no42" in cif_data.filename:
        return  # Reconstructed with different wrapping?
    np.testing.assert_allclose(parsnip_positions, ase_positions, atol=1e-12)


@cif_files_mark
def test_invalid_unit_cell(cif_data):
    if "PDB" in cif_data.filename:
        return

    previous_alpha = cif_data.file.pairs["_cell_angle_alpha"]
    cif_data.file._pairs["_cell_angle_alpha"] = "180"

    with pytest.raises(ValueError, match="outside the valid range"):
        cif_data.file.build_unit_cell()
    cif_data.file._pairs["_cell_angle_alpha"] = previous_alpha


@pytest.mark.parametrize(
    "filename",
    [
        *[cif.filename for cif in cif_files_mark.kwargs["argvalues"]],
        *[cif.filename for cif in additional_data_array],
    ],
)
@pytest.mark.parametrize("n_decimal_places", [3, 4])
def test_build_accuracy(filename, n_decimal_places):
    if (
        "A5B10C8D4_mC108_15_a2ef_5f_4f_2f.cif" in filename
        or "A2B2CD2_oP14_34_c_c_a_c.cif" in filename
        or ("A12B36CD12_cF488_210" in filename and n_decimal_places == 4)
    ):
        pytest.xfail(reason="Known failing structure found.")

    def parse_pearson(p) -> tuple[bool, int]:
        if p is None:
            return (False, -1)
        return (p.strip("'")[:2] == "hR", int(re.sub(r"[^\w]", "", p)[2:]))

    warnings.filterwarnings("ignore", category=ParseWarning)
    cif = CifFile(filename)

    if cif["*Pearson"] is None:
        return
    (is_rhombohedral, n), uc = (
        parse_pearson(cif["*Pearson"]),
        cif.build_unit_cell(n_decimal_places=n_decimal_places, parse_mode="sympy"),
    )
    uc = np.array(sorted(uc, key=lambda x: tuple(x)))
    msg = "cell does not match Pearson symbol!"
    if not is_rhombohedral:
        np.testing.assert_equal(len(uc), n, err_msg=msg)
    else:  # AFlow rhombohedral structures include data for hexagonal setting
        np.testing.assert_equal(len(uc), 3 * n, err_msg=msg)
