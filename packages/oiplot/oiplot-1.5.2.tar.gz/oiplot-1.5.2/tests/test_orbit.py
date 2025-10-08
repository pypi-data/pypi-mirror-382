import numpy as np
import pytest

from oiplot import orbit


@pytest.mark.parametrize(
    "mean_anomaly, eccentricity, expected", [(5, 0.1, 5.554589), (2, 0.99, 32.361007)]
)
def test_solve_eccentric_anomaly(mean_anomaly, eccentricity, expected):
    """Test the eccentricity solve."""
    E = np.rad2deg(
        orbit.solve_eccentric_anomaly(np.deg2rad(mean_anomaly), eccentricity)
    )
    assert np.isclose(E, expected, atol=1e-6)


def test_compute_true_anomaly(mean_anomaly, eccentricity, expected):
    """Test computation of the true anomaly."""
    E = np.rad2deg(
        orbit.solve_eccentric_anomaly(np.deg2rad(mean_anomaly), eccentricity)
    )
    true_anomaly = orbit.compute_true_anomaly(E, eccentricity)


# def test_get_epoch(, ):
#     ...
