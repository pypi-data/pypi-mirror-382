import re
import copy
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Dict, List, Tuple

import astropy.units as u
import numpy as np
from numpy.typing import ArrayLike
import pandas as pd
from astropy.io import fits
from astropy.utils.masked import Masked


def read(
    files_or_hduls: Path | List[Path] | List[fits.HDUList],
) -> List[fits.HDUList]:
    """Reads in a list of OIFITS files or copies them if already opened.

    Parameters
    ----------
    files_or_hduls : Path or list of Path or list of astropy.io.fits.HDUList

    Returns
    -------
    list of astropy.io.fits.HDUList
    """
    if not isinstance(files_or_hduls, Iterable):
        files_or_hduls = [files_or_hduls]

    hduls = []
    for fits_file in files_or_hduls:
        if isinstance(fits_file, fits.HDUList):
            hdul = fits_file
        elif isinstance(fits_file, Path):
            with fits.open(fits_file) as hdul:
                hdul = copy.deepcopy(hdul)
        else:
            raise ValueError(
                "Input must be a Path or HDUList or an iterable containing those."
            )

        hduls.append(hdul)
    return hduls


def sort(hduls: List[fits.HDUList], by: str | List[str]) -> List[fits.HDUList]:
    """Sorts a list of astropy.io.fits.HDUList.

    Parameters
    ----------
    hduls : list of astropy.io.fits.HDUList
    by : str or list of str
        The key by which is sorted.

    Returns
    -------
    sorted_hduls : list of astropy.io.fits.HDUList
    """
    by = [by] if not isinstance(by, (tuple, list, np.ndarray)) else by
    data = {
        "index": range(len(hduls)),
        **{key: [get(hdul, key) for hdul in hduls] for key in by},
    }
    return [hduls[i] for i in pd.DataFrame(data).sort_values(by=by)["index"].tolist()]


def filter(hduls: List[fits.HDUList], by: Dict[str, Any]) -> List[fits.HDUList]:
    """Filters a list of fits.HDUList.

    Parameters
    ----------
    hduls : list of astropy.io.fits.HDUList
    by : dict of str
        The filter condition.

    Returns
    -------
    filtered_hduls : list of astropy.io.fits.HDUList
    """
    df = pd.DataFrame(
        {
            "index": range(len(hduls)),
            **{key: [get(hdul, key) for key in by.keys() for hdul in hduls]},
        }
    )

    for key, value in by.items():
        df = df[df[key] == value]

    return [hduls[i] for i in df["index"].tolist()]


def _parse_key(key: str) -> Tuple[str, int, str, str]:
    """Parses a key.

    Parameters
    ----------
    key : str
        Parses a key of the format "<extension>:<extver>.<key_or_column>.<attribute>"
        (e.g. "OI_VIS:10.UCOORD.UNIT"). One can combine all terms freely with <key_or_column>.

    Returns
    -------
    extension : str, optional
        The extension name.
    version : int, optional
        The extension version number.
    column_or_key : str, optional
        Either a header key or column name.
    attribute : str, optional
        A column attribute (e.g. unit, etc.).
    """
    extension, key_or_column, attribute = [None] * 3
    version = re.findall(r":(\d+\.?\d*)", key)
    if version:
        version = int(version[0][:-1] if version[0][-1] == "." else version[0])
        key = key.replace(f":{version}", "")
    else:
        version = 1

    if "." in key:
        split_key = key.split(".")
        if any(c in split_key[0] for c in ["PRIMARY", "OI"]):
            extension = split_key.pop(0)

        if len(split_key) == 2:
            key_or_column, attribute = split_key
        else:
            key_or_column = split_key[0]
    else:
        key_or_column = key

    return extension, version, key_or_column, attribute


# TODO: Make this more robust for non-findings?
# TODO: Check mask and unit work with oi_array as well
# TODO: Make documentation for all the features
# TODO: Make it possible to determine default (not only None as return value)
def get(
    hdul: fits.HDUList, key: str, **kwargs
) -> str | bool | int | float | ArrayLike | None:
    """Fetches anything from an OIFITS file by the key.
    This can be an HDU, a header entry, or a column.

    Parameters
    ----------
    hdul : astropy.io.fits.HDUList
        An opened OIFITS file.
    key : str
        Can be any (case-insensitve) OIFITS keyword (e.g. "OI_VIS", "VISAMP").
        For more control the key can be "<extension>:<extver>.<key_or_column>.<attribute>"
        (e.g. "OI_VIS:10.UCOORD.UNIT"). One can combine all terms freely with <key_or_column>.
    mask : bool, optional
        If True, applies the flags and returns the columns as an
        astropy.utils.masked.Masked array. If there are no flags, returns a numpy.ndarray.
        Default is "True".
    unit : bool, optional
        If True, returns the column as an astropy.units.Quantity.
        If there is no unit, it will return a numpy.ndarray.
        Default is "True".

    Returns
    -------
    query_result : any
        Returns the result from the OIFITS query or None.

    Warning
    -------
    If no version is specified, the first matching extension is returned.
    """
    extension, version, key_or_column, attribute = _parse_key(key.upper())
    # TODO: Key or column is not quite clean here -> Improve this
    for hdu in hdul:
        if key_or_column == hdu.name:
            extension, key_or_column = hdu.name, None
        elif key_or_column in hdu.header.keys():
            extension = hdu.name
        elif hdu.name != "PRIMARY":
            if key_or_column in hdu.columns.names:
                extension = hdu.name

        if extension is not None:
            break

    if extension is None or extension not in hdul:
        return None

    hdu = hdul[extension, version]
    if key_or_column is None:
        return hdu

    if key_or_column in hdu.header.keys():
        return hdu.header[key_or_column]

    # TODO: Maybe this needs to more robust, if no key like attribute.lower()?
    if attribute is not None:
        return getattr(hdu.columns[key_or_column], attribute.lower())

    values = hdu.data[key_or_column]
    mask_default = "FLAG" in hdu.columns.names and "COORD" not in key_or_column
    if kwargs.get("mask", mask_default):
        values = Masked(values, mask=hdu.data["flag"])

    # TODO: Finish tests for this and also make it more robust
    if kwargs.get("unit", True):
        unit = hdu.columns[key_or_column].unit
        values *= u.Unit(unit if unit not in ["ADU"] else unit.lower())
    return values


# TODO: Finish this
def set(hdul: fits.HDUList, key: str, value: Any) -> None:
    """Sets arrays or units for the keyword in the header.

    Parameters
    ----------
    hdul : astropy.io.fits.HDUList
        An opened OIFITS file.
    key : str
        Can be any (case-insensitve ) OIFITS2 keyword (e.g. "OI_VIS", "VISAMP") or
        a combination in the following way "OI_VIS.header.<header_key>",
        "OI_VIS.VISAMP", etc.
    value : any
        The value to be set.
    """
    ...
