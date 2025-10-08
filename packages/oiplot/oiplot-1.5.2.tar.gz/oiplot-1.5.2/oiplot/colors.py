from typing import List

import matplotlib.pyplot as plt
from matplotlib import colormaps as mcm
from matplotlib.colors import ListedColormap


def convert_style_to_colormap(style: str) -> ListedColormap:
    """Converts style to colormap.

    Parameters
    ----------
    style : str
        A matplotlib style.

    Returns
    -------
    colormap : matplotlib.colors.ListedColormap
    """
    plt.style.use(style)
    colormap = ListedColormap(plt.rcParams["axes.prop_cycle"].by_key()["color"])
    plt.style.use("default")
    return colormap


def get_colormap(colormap_or_style: str) -> ListedColormap:
    """Gets a colormap via the input name or style.

    Parameters
    ----------
    colormap_or_style : str
        The name of a colormap.

    Returns
    -------
    colormap : matplotlib.colors.ListedColormap
    """
    try:
        return mcm.get_cmap(colormap_or_style)
    except ValueError:
        return convert_style_to_colormap(colormap_or_style)


def get_colorlist(colormap: str, ncolors: int | None) -> List[str]:
    """Gets a list of colors from a colormap.

    Parameters
    ----------
    colormap : str
        The colormap to sample the colors from.
    ncolors : int, optional
        The number of colors to sample.

    Returns
    -------
    colors : list of str
    """
    return [get_colormap(colormap)(i) for i in range(ncolors)]
