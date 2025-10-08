from typing import List, Tuple

import numpy as np
from numpy.typing import ArrayLike

from .utils import rotate


def get_normal(polar: float, azimuth: float) -> ArrayLike:
    """Gets the normal vector for a polar and azimuth angle.

    Parameters
    ----------
    pola: float
        The polar angle (radians).
    pa: float
        The azimuth angle (radians).

    Returns
    -------
    normal : array_like
    """
    return np.array(
        [
            -np.sin(polar) * np.sin(azimuth),
            np.sin(polar) * np.cos(azimuth),
            np.cos(polar),
        ]
    )


def line(scale: float, angle: float) -> ArrayLike:
    """Returns a scaled and rotated unit vector from origin.

    Parameters
    ----------
    scale : float
    angle : float

    Returns
    -------
    line : array_like
    """
    return rotate(np.array([0, 0]), np.array([-0.5, 0.5]) * scale, angle)


def ring(
    rin: float,
    i: float = 0.0,
    pa: float = 0.0,
    resolution: int = 512,
    centre: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    dim: str = "3D",
) -> ArrayLike:
    """Computes a ring dependent on the normal of the polar/inclination
    and azimuthal/position angles.

    Parameters
    ----------
    rin : float
        The inner radius of the ring.
    resolution : float
        The resolution of the ring.
    i: float, optional
        The inclination angle (radians). Default is 0.
    pa : float, optional
        The position angle. Default is 0.
    centre : tuple of floats
        The centre of the disc. Default is (0, 0, 0).
        In case of a 2D disc, the third coordinate is ignored.
    dim : str, optional

    Returns
    -------
    ring : array_like
    """
    normal = get_normal(i, pa)
    base1 = np.cross(normal, [1, 0, 0])
    base1 /= np.linalg.norm(base1)
    base2 = np.cross(normal, base1)
    base2 /= np.linalg.norm(base2)
    theta = np.linspace(0, 2 * np.pi, resolution)

    if dim == "3D":
        ring = np.array(
            [
                np.array(centre) + rin * (np.cos(t) * base1 + np.sin(t) * base2)
                for t in theta
            ]
        )
    else:
        a, b = rin, rin * np.cos(normal[-1])
        pa = np.arctan2(normal[1], normal[0])
        ring = rotate(a * np.cos(theta), b * np.sin(theta), pa)
    return ring


def disc(
    radii: List[float],
    i: float = 0.0,
    pa: float = 0.0,
    pixel_size=0.1,
    resolution: int = 2048,
) -> ArrayLike:
    """Computes a disc dependent on inclination and position angle.

    Parameters
    ----------
    radii : list of float
        The radii that makes up the disc.
    i: float, optional
        The inclination angle (radians). Default is 0.
    pa : float, optional
        The position angle. Default is 0.
    resolution : float
        The resolution of the ring.

    Returns
    -------
    disc : array_like
    """
    x = np.linspace(-0.5, 0.5, resolution) * pixel_size
    xx, yy = np.meshgrid(x, x, sparse=True)

    # TODO: Replace this with the "transformat_coordinate" function
    xt = (xx * np.cos(pa) - yy * np.sin(pa)) * np.cos(i)
    yt = xx * np.sin(pa) + yy * np.cos(pa)
    grid = np.hypot(xt, yt)

    profiles = []
    for i in range(len(radii) - 1):
        if i % 2 == 0:
            profiles.append(((grid >= radii[i]) & (grid < radii[i + 1])))

    return np.logical_or.reduce(profiles).astype(int)
