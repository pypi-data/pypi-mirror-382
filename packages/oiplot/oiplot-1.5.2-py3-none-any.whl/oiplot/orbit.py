from typing import Tuple
import numpy as np
import astropy.units as u
from astropy.time import Time


def solve_eccentric_anomaly(mean_anomaly: float, eccentricity: float) -> float:
    """Numerically solves the eccentric anomaly.

    Parameters
    ----------
    mean_anomaly : float
    eccentricity : float

    Returns
    -------
    eccentric_anomaly : float

    Notes
    -----
    Equations from J. Meeus+1991, Chapter 29, third method.
    """
    mean_anomaly %= 2 * np.pi
    if mean_anomaly > np.pi:
        mean_anomaly = 2 * np.pi - mean_anomaly
        sign = -1
    else:
        sign = 1

    e0, d0 = np.pi / 2, np.pi / 4
    for _ in range(33):
        m1 = e0 - eccentricity * np.sin(e0)
        e0 = e0 + d0 * np.sign(mean_anomaly - m1)
        d0 /= 2

    return e0 * sign


def compute_true_anomaly(eccentric_anomaly: float, eccentricity: float) -> float:
    """Computes the true anomaly.

    Parameters
    ----------
    eccentric_anomaly : float
    eccentricity : float

    Returns
    -------
    true_anomaly : float
    """
    return 2 * np.arctan(
        np.sqrt((1 + eccentricity) / (1 - eccentricity)) * np.tan(eccentric_anomaly / 2)
    )


def convert_date_to_epoch(date: str) -> float:
    """Converts an iso date string to a floating point number
    of the form <year>.<percentage>.

    Parameters
    ----------
    date : str

    Returns
    -------
    date : float
    """
    return Time(date, format="iso").decimalyear


def get_epoch(
    epoch: u.yr,
    period: u.yr,
    eccentricity: float,
    semi_major_axis: u.Quantity,
    inclination: u.deg,
    time: u.yr,
    omega: u.deg,
    Omega: u.deg,
) -> Tuple[u.Quantity, u.deg]:
    """Computes the position of the companion at a certain epoch/time.

    Parameters
    ----------
    epoch : astropy.units.year
        The epoch/time of the companion.
    period : astropy.units.year
        The period of revolution expressed in solar years.
    eccentricity : float
        The eccentricity of the true orbit.
    semi_major_axis : astropy.units.Quantity
        The semi-major axis of the true orbit.
    inclination : astropy.units.deg
        The inclination of the plane of the true orbit to the plane at the
        right angles to the line of sight. For direct motion in the apparent
        orbit it ranges from 0 to 90 and for retrograde motion it is between
        90 and 180 degrees. When it is 90, the apparent orbit is a straight line
        passing through the primary star.
    ttime : astropy.units.yr
        The time of perihelion passage, generally given as year and decimal.
    omega : astropy.units.deg
        The longitude of the periastron. The angle in the plane of the true
        orbit measured from the ascending node to the periastron, taken always
        in the direction of motion.
    Omega : astropy.units.deg
        The position angle of the long long ascending node.

    Returns
    -------
    rho : astropy.units.Quantity
        The separation of the primary and the companion in units of the semi-major axis.
    theta : astropy.units.deg
        The position angle of the companion.

    Notes
    -----
    Equations from J. Meeus+1991, Chapter 55, binary stars.
    """
    M = 2 * np.pi * (epoch - time) / period
    E = solve_eccentric_anomaly(M.value, eccentricity.value)
    nu = compute_true_anomaly(E, eccentricity)

    # NOTE: Up to here soley Kepler, see Chapter 55 for these calculations
    argument = nu + omega.to(u.rad)
    x = np.arctan2(
        np.sin(argument) * np.cos(inclination),
        np.cos(argument),
    )
    theta = (x + Omega.to(u.rad)).to(u.deg)
    radius = semi_major_axis * (1 - eccentricity * np.cos(E))
    rho = radius * np.cos(argument) / np.cos(x)
    return rho, theta


def get_orbit(
    period: u.yr,
    eccentricity: u.one,
    semi_major_axis: u.Quantity,
    inclination: u.deg,
    time: u.yr,
    omega: u.deg,
    Omega: u.deg,
    sampling: int = 1024,
) -> Tuple[u.Quantity, u.deg]:
    """Computes the position of the companion at a certain epoch/time.

    Parameters
    ----------
    period : astropy.units.year
        The period of revolution expressed in solar years.
    eccentricity : float
        The eccentricity of the true orbit.
    semi_major_axis : astropy.units.Quantity
        The semi-major axis of the true orbit.
    inclination : astropy.units.deg
        The inclination of the plane of the true orbit to the plane at the
        right angles to the line of sight. For direct motion in the apparent
        orbit it ranges from 0 to 90 and for retrograde motion it is between
        90 and 180 degrees. When it is 90, the apparent orbit is a straight line
        passing through the primary star.
    t : astropy.units.yr
        The time of perihelion passage, generally given as year and decimal.
    omega : astropy.units.deg
        The longitude of the periastron. The angle in the plane of the true
        orbit measured from the ascending node to the periastron, taken always
        in the direction of motion.
    Omega : astropy.units.deg
        The position angle of the long long ascending node.
    sampling : int, optional
        The point sampling of the orbit (always <= period).

    Returns
    -------
    rhos : astropy.units.Quantity
        The separations of the primary and the companion in units of the semi-major axis.
    theta : astropy.units.deg
        The position angles of the companion.
    """
    if sampling < period.value:
        sampling = int(np.ceil(period.value))

    rhos, thetas = [], []
    for epoch in np.linspace(time, time + period, sampling):
        rho, theta = get_epoch(
            epoch,
            period,
            eccentricity,
            semi_major_axis,
            inclination,
            time,
            omega,
            Omega,
        )
        rhos.append(rho)
        thetas.append(theta)

    return u.Quantity(rhos), u.Quantity(thetas)
