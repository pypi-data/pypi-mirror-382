from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple

import astropy.units as u
import numpy as np
import yaml
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

PREFIXES = np.load(Path(__file__).parent / "config" / "prefixes.npy").tolist()


def get_labels(input_list: List[Any]) -> List[str]:
    """Gets unique identifiers for elements of a list.

    Parameters
    ----------
    input_list : list of any

    Returns
    -------
    list of str
    """
    return [f"{chr(ord('A') + i)}" for i, _ in enumerate(input_list)]


def get_prefix(value: u.Quantity) -> str:
    """Gets the unit prefix from the passed value.

    Parameters
    ----------
    value : astropy.units.Quantity

    Returns
    -------
    prefix : str
    """
    base = value.decompose().value
    for prefix, exp in zip(PREFIXES, range(-27, 33, 3)):
        if base < 10**exp:
            return prefix
    return PREFIXES[-1]


def get_figsize(
    textwidth: float = 7.24551,
    aspect_ratio: float = 6 / 8,
    scale: float = 1.0,
) -> Tuple[float, float]:
    """Gets the figsize (inch) for a certain textwidth.

    Returns
    -------
    width : float, optional
    height : float, optional
    scale : float, optional

    Returns
    -------
    width : float
    height : float

    Notes
    -----
    Defaults to the A&A, two-column layout.
    """
    width = textwidth * scale
    return width, width * aspect_ratio


# TODO: Make this possible for 2D as well
def rotate(x: Any, y: Any, pa: float) -> ArrayLike:
    """Rotates vectors via an angle."""
    return (
        np.vstack([x, y]).T
        @ np.array([[np.cos(pa), -np.sin(pa)], [np.sin(pa), np.cos(pa)]])
    ).T


def get_extent(dim: int, pixel_size: float = 1.0) -> ArrayLike:
    """Gets the extent of a grid/image.

    Parameters
    ----------
    dim : int
    pixel_size : float, optional

    Returns
    -------
    array_like
    """
    return np.array([-1, 1, -1, 1]) * 0.5 * dim * pixel_size


def read_yaml_to_namespace(file_name: Path) -> SimpleNamespace:
    """Reads a yaml file and returns a dictionary.
    Also converts all units from strings to astropy.units.

    Parameters
    ----------
    file_name : pathlib.Path

    Returns
    -------
    content : types.SimpleNamespace
    """
    with open(file_name, "r") as file:
        content = yaml.safe_load(file)

    for key, val in content.items():
        if not isinstance(val, dict):
            continue

        for k, v in val.items():
            if "unit" in k:
                if isinstance(v, dict):
                    v = {i: u.Unit(j) for i, j in v.items()}
                else:
                    v = u.Unit(v)

            content[key][k] = SimpleNamespace(**v) if isinstance(v, dict) else v
        content[key] = SimpleNamespace(**val) if isinstance(val, dict) else val

    return SimpleNamespace(**content)


def inset_at_point(
    ax: Axes,
    x: int | float,
    y: int | float,
    width: int | float,
    height: int | float,
) -> Axes:
    """Insets a plot into an axis at certain data coordinates.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    x : int or float
        The x position (percentage).
    y : int or float
        The y position (percentage).
    width : int or float
    height : int or float

    Returns
    -------
    inset_ax : matplotlib.axes.Axes
    """
    return ax.inset_axes(
        (x - width / 2, y - height / 2, width, height), transform=ax.transData
    )


# TODO: Add colorbar support here (and setting limits via the collections)
def _axplot(
    ax: Axes,
    x: ArrayLike,
    y: ArrayLike,
    yerr: ArrayLike,
    z: ArrayLike | None = None,
    errorbar: bool = False,
    kwargs_inset: Dict[str, Any] = {},
    **kwargs,
) -> Axes:
    """Plots data.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis to be plotted on.
    x : array_like
        The x data.
    y : array_like
        The y data.
    z : array_like, optional
        The z data.
    errorbar : bool, optional
        If "True" plots the errorbars as filled area.
        Default is False.
    kwargs_inset : dict
        Keyword arguments for the inset axes.
        Default is {"show_axis": True, "inset_width": 0.2,
        "inset_height": 0.2, "inset_point": None}.

    Returns
    -------
    ax : matplotlib.axes.Axes
    """
    show_axis = kwargs_inset.get("show_axis", True)
    width, height = kwargs_inset.get("inset_width", 0.2), kwargs_inset.get(
        "inset_height", 0.2
    )
    if (inset_point := kwargs.pop("inset_point", None)) is not None:
        ax = inset_at_point(ax, *inset_point, width, height)
        ax.axis("on" if show_axis else "off")

    line = ax.plot(x, y, **kwargs)[0]
    if errorbar:
        ax.fill_between(
            x,
            y + yerr,
            y - yerr,
            alpha=kwargs.get("alpha", 0.5),
            color=line.get_color(),
        )
    return ax


def get_plot_layout(nplots: int) -> Tuple[int, int]:
    """Returns the optimal number of rows and columns for
    a given number of plots.

    Parameters
    ----------
    nplots : int

    Returns
    -------
    rows : int
    cols : int
    """
    sqrt_nplots = np.sqrt(nplots)
    rows, cols = int(np.floor(sqrt_nplots)), int(np.ceil(sqrt_nplots))

    while rows * cols < nplots:
        if cols < rows:
            cols += 1
        else:
            rows += 1

    while (rows - 1) * cols >= nplots:
        rows -= 1

    return rows, cols


def transform_coordinates(
    x: float | ArrayLike,
    y: float | ArrayLike,
    cinc: float | None = 1,
    pa: float = 0,
    axis: str = "y",
) -> Tuple[float | ArrayLike, float | ArrayLike]:
    """Stretches and rotates the coordinate space depending on the
    cosine of inclination and the positional angle.

    Parameters
    ----------
    x: float or array_like
        The x-coordinate.
    y: float or array_like
        The y-coordinate.
    cinc: float, optional
        The cosine of the inclination.
    pa: float, optional
        The positional angle of the object (in degree).
    axis: str, optional
        The axis to stretch the coordinates on.

    Returns
    -------
    xt: float or array_like
        Transformed x coordinate.
    yt: float or array_like
        Transformed y coordinate.
    """
    xt, yt = rotate(x, y, pa)
    if cinc is not None:
        if axis == "x":
            xt /= cinc
        elif axis == "y":
            xt *= cinc

    return xt, yt
