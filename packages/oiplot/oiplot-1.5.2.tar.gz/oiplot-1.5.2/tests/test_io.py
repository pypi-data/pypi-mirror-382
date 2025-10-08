from pathlib import Path

import numpy as np
from astropy.utils.masked import Masked

import pytest
from oiplot import io


@pytest.fixture
def pionier_file():
    return Path(__file__).parent.parent / "data" / "fits_files" / "PIONIER.fits"


def test_read() -> None: ...


def test_get(pionier_file: Path) -> None:
    """Tests the "io.get" function."""
    hdul = io.read(pionier_file)[0]
    date = hdul[0].header["DATE-OBS"]
    values = hdul["oi_vis"].data["visamp"]
    masked_values = Masked(values, mask=hdul["oi_vis"].data["flag"])

    assert io.get(hdul, "primary.date-obs") == io.get(hdul, "date-obs") == date
    assert io.get(hdul, "oi_vis") == hdul["oi_vis"]
    assert np.array_equal(io.get(hdul, "visamp", mask=False, unit=False), values)
    assert np.array_equal(io.get(hdul, "visamp", unit=False), masked_values)
    # TODO: Make tests for units as well

    assert np.array_equal(io.get(hdul, "oi_vis.visamp", mask=False, unit=False), values)
    assert np.array_equal(io.get(hdul, "oi_vis.visamp", unit=False), masked_values)
    assert io.get(hdul, "t3phi.name") == hdul["oi_t3"].columns["t3phi"].name
    assert io.get(hdul, "t3phi.format") == hdul["oi_t3"].columns["t3phi"].format
    assert io.get(hdul, "t3phi.unit") == hdul["oi_t3"].columns["t3phi"].unit
    assert io.get(hdul, "oi_t3.t3phi.name") == hdul["oi_t3"].columns["t3phi"].name
    assert io.get(hdul, "oi_t3.t3phi.format") == hdul["oi_t3"].columns["t3phi"].format
    assert io.get(hdul, "oi_t3.t3phi.unit") == hdul["oi_t3"].columns["t3phi"].unit

    # TODO: Make tests with GRAViTY files for the version
    # assert io.get(hdul, "oi_vis:1") ==
