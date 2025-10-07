import numpy as np
import pytest

from astropy import units as u
from astropy.time import Time
from astropy.wcs import WCS

from ndcube.meta import NDMeta

from irispy import SJICube, utils

TIMES = Time(["2014-12-11T19:39:00.48", "2014-12-11T19:43:07.6"])
EXTRA_COORDS = [("time", 0, TIMES)]


@pytest.fixture
def cube():
    data = np.array(
        [
            [[1, 2, 3, 4], [2, 4, 5, 3], [0, 1, 2, 3]],
            [[2, 4, 5, 1], [10, 5, 2, 2], [10, 3, 3, 0]],
        ],
    )
    exposure_times = 2 * np.ones((2), float) * u.s
    uncertainty = np.sqrt(data)
    header = {
        "CTYPE1": "HPLN-TAN",
        "CUNIT1": "arcsec",
        "CDELT1": 0.4,
        "CRPIX1": 0,
        "CRVAL1": 0,
        "NAXIS1": 4,
        "CTYPE2": "HPLT-TAN",
        "CUNIT2": "arcsec",
        "CDELT2": 0.5,
        "CRPIX2": 0,
        "CRVAL2": 0,
        "NAXIS2": 3,
        "CTYPE3": "Time    ",
        "CUNIT3": "s",
        "CDELT3": 0.3,
        "CRPIX3": 0,
        "CRVAL3": 0,
        "NAXIS3": 2,
    }
    wcs = WCS(header=header, naxis=3)
    cube = SJICube(
        data,
        wcs,
        uncertainty=uncertainty,
        mask=data >= 0,
        unit=utils.constants.DN_UNIT["SJI"],
        scaled=True,
        meta=NDMeta({"exposure time": exposure_times}, axes={"exposure time": 0}, data_shape=data.shape),
    )
    cube.extra_coords.add(*EXTRA_COORDS[0])
    return cube


@pytest.fixture
def cube_2d():
    data_2d = np.array([[1, 2, 3, 4], [2, 4, 5, 3]])
    uncertainty_2d = np.sqrt(data_2d)
    header_2d = {
        "CTYPE1": "HPLN-TAN",
        "CUNIT1": "arcsec",
        "CDELT1": 0.4,
        "CRPIX1": 0,
        "CRVAL1": 0,
        "NAXIS1": 4,
        "CTYPE2": "HPLT-TAN",
        "CUNIT2": "arcsec",
        "CDELT2": 0.5,
        "CRPIX2": 0,
        "CRVAL2": 0,
        "NAXIS2": 3,
    }
    exposure_times = 2 * np.ones((2), float) * u.s
    wcs_2d = WCS(header=header_2d, naxis=2)
    cube_2d = SJICube(
        data_2d,
        wcs_2d,
        uncertainty=uncertainty_2d,
        mask=data_2d >= 0,
        unit=utils.constants.DN_UNIT["SJI"],
        scaled=True,
        meta=NDMeta({"exposure time": exposure_times}, axes={"exposure time": 0}, data_shape=data_2d.shape),
    )
    cube_2d.extra_coords.add(*EXTRA_COORDS[0])
    return cube_2d


@pytest.fixture
def cube_1d():
    header_1d = {
        "CTYPE1": "Time    ",
        "CUNIT1": "s",
        "CDELT1": 0.4,
        "CRPIX1": 0,
        "CRVAL1": 0,
        "NAXIS1": 2,
    }
    exposure_times = 2 * np.ones((2), float) * u.s
    wcs_1d = WCS(header=header_1d, naxis=1)
    data_1d = np.array([1, 2])
    cube_1d = SJICube(
        data_1d,
        wcs_1d,
        uncertainty=np.sqrt(np.array([1, 2])),
        mask=data_1d >= 0,
        unit=utils.constants.DN_UNIT["SJI"],
        scaled=True,
        meta=NDMeta({"exposure time": exposure_times}, axes={"exposure time": 0}, data_shape=data_1d.shape),
    )
    cube_1d.extra_coords.add(*EXTRA_COORDS[0])
    return cube_1d


@pytest.fixture
def dust_cube():
    data_dust = np.array(
        [
            [[-1, 2, -3, 4], [2, -200, 5, 3], [0, 1, 2, -300]],
            [[2, -200, 5, 1], [10, -5, 2, 2], [10, -3, 3, 0]],
        ],
    )
    header = {
        "CTYPE1": "HPLN-TAN",
        "CUNIT1": "arcsec",
        "CDELT1": 0.4,
        "CRPIX1": 0,
        "CRVAL1": 0,
        "NAXIS1": 4,
        "CTYPE2": "HPLT-TAN",
        "CUNIT2": "arcsec",
        "CDELT2": 0.5,
        "CRPIX2": 0,
        "CRVAL2": 0,
        "NAXIS2": 3,
        "CTYPE3": "Time    ",
        "CUNIT3": "s",
        "CDELT3": 0.3,
        "CRPIX3": 0,
        "CRVAL3": 0,
        "NAXIS3": 2,
    }
    wcs = WCS(header=header, naxis=3)
    unit = utils.constants.DN_UNIT["SJI"]
    mask_dust = data_dust == -200

    uncertainty = 1
    times = Time(["2014-12-11T19:39:00.48", "2014-12-11T19:43:07.6"])
    exposure_times = 2 * np.ones((2), float) * u.s
    extra_coords = [("time", 0, times)]
    scaled_T = True
    meta = NDMeta(
        {"exposure time": exposure_times, "OBSID": 1},
        axes={"exposure time": 0},
        data_shape=data_dust.shape,
    )
    dust_cube = SJICube(
        data_dust,
        wcs,
        uncertainty=uncertainty,
        mask=mask_dust,
        unit=unit,
        scaled=scaled_T,
        meta=meta,
    )
    dust_cube.extra_coords.add(*extra_coords[0])
    return dust_cube


def test_sjicube_apply_dust_mask(dust_cube):
    # TODO: The expected values are not correct.
    dust_mask_expected = np.array(
        [
            [[True, True, True, True], [True, True, True, True], [True, True, False, False]],
            [[True, True, True, False], [True, True, True, True], [True, True, True, True]],
        ]
    )
    dust_cube.apply_dust_mask()
    np.testing.assert_array_equal(dust_cube.mask, dust_mask_expected)
    dust_cube.apply_dust_mask(undo=True)
    before_mask = np.array(
        [
            [[False, False, False, False], [False, False, False, False], [False, False, False, False]],
            [[False, False, False, False], [False, False, False, False], [False, False, False, False]],
        ]
    )
    np.testing.assert_array_equal(dust_cube.mask, before_mask)
