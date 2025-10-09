# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import types
import warnings

import numpy as np
from scipy.interpolate import RectBivariateSpline, interp1d
from scipy.signal import convolve

from .predefined_k_grids import k_fast, k_precise


def check_diff(diff, thresh):
    return np.any(diff[np.isfinite(diff)] > thresh)


class PerturbationTable:
    """
    This class has been written to handle operations involving building tabulated data.
    For some of the calculations this is often useful. These tables can then be accessed
    through interpolation routines rather than doing the full calculations repeatedly.
    """

    def __init__(self, cosmo, perturbation):
        self._cosmo = cosmo
        self._params = cosmo.params
        self._perturbation = perturbation
        self._interpolator = None

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        if self._interpolator is None:
            self._setup_interpolator()

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)

        if np.min(a) < self._a_limits[0] or np.max(a) > self._a_limits[1]:
            raise ValueError(f"found a values outside range {self._a_limits}")
        if np.min(k) < self._k_limits[0] or np.max(k) > self._k_limits[1]:
            raise ValueError(f"found k values outside range {self._k_limits}")

        if diag_only:
            if len(a) != len(k):
                raise ValueError(
                    "for diag_only=True a and k vectors must have same length"
                )
            return np.exp(self._interpolator(np.log(a), np.log(k), grid=False))
        return np.exp(self._interpolator(np.log(a), np.log(k), grid=True)).T

    def __getattr__(self, name):
        if isinstance(getattr(self._perturbation, name, None), types.MethodType):
            # this makes sure that the method calls within self._perturbation
            # still are fowarded to this class:
            def method(*a, **kw):
                return getattr(self._perturbation.__class__, name)(self, *a, **kw)

            return method
        else:
            try:
                return getattr(self._perturbation, name)
            except AttributeError:
                raise AttributeError(
                    f"{self._perturbation} has no attribute {name}"
                ) from None

    def __getstate__(self):
        # see https://stackoverflow.com/questions/50888391
        return self.__dict__

    def __setstate__(self, state):
        # see https://stackoverflow.com/questions/50888391
        self.__dict__.update(state)

    def _setup_interpolator(self):
        self._k_grid = self._interp_grid_k()
        self._a_grid = self._interp_grid_a()

        lnk_grid = np.log(self._k_grid)

        min_a = np.max(self._perturbation.min_a(self._k_grid))

        valid_a = self._a_grid[self._a_grid > min_a]

        self._a_limits = (np.min(valid_a), np.max(valid_a))
        values = self._perturbation.powerspec_a_k(valid_a, self._k_grid)
        self._interpolator = RectBivariateSpline(
            np.log(valid_a),
            lnk_grid,
            np.log(values.T),
        )

    def _interp_grid_k(self):
        tabulation = self._params.tabulation

        if tabulation == "bao":
            c = self._cosmo
            k_wiggles = np.pi / (c.background.r_s() / c.params.h)
            k_first = 10 ** np.linspace(-5, np.log10(k_wiggles), 10)

            h = np.pi / 5
            n = 22
            k_middle = k_wiggles * np.arange(1, n / h) * h

            k_last = 10 ** np.linspace(np.log10(k_middle[-1]), 2, 10)

            k_grid = np.hstack((k_first, k_middle, k_last))

        elif tabulation == "manual":
            k_grid = self._params.tabulation_k_grid
            assert k_grid is not None, (
                "you must set the parameter tabulation_k_grid if you use manual"
                " tabulation"
            )

        elif tabulation == "default_precise":
            k_grid = k_precise

        elif tabulation == "default_fast":
            k_grid = k_fast

        else:
            raise ValueError(f"invalid setting for tabulation: {tabulation}")

        min_k = self._params.tabulation_min_k
        max_k = self._params.tabulation_max_k

        if min_k < np.min(k_grid):
            warnings.warn(
                f"ignore tabulation_min_k value {min_k} which is below the smallest"
                f" value {np.min(k_grid)} in the chosen k grid"
            )

        if np.max(k_grid) < max_k:
            warnings.warn(
                f"ignore tabulation_max_k value {max_k} which is beyond the largest"
                f" value {np.max(k_grid)} in the chosen k grid"
            )

        k_grid = k_grid[k_grid >= min_k]
        k_grid = k_grid[k_grid <= max_k]

        self._k_limits = (np.min(k_grid), np.max(k_grid))
        # remove duplicates in log values:
        return sorted({np.log(k): k for k in k_grid}.values())

    def _interp_grid_a(self):
        lna_min = -17
        lna_max = 0.0
        lna_grid = np.linspace(lna_min, lna_max, 1000)
        return np.exp(lna_grid)


def optimize_grid(perturbation, initial_k_grid, tolerance, width, pk_tobe=None):
    if pk_tobe is None:
        pk_tobe = perturbation.powerspec_a_k(1.0, initial_k_grid).flatten()
    kgrid, pk_local = _thinout(initial_k_grid, pk_tobe, tolerance, width)
    ip = _buildip(kgrid, pk_local)
    pk_ip = _evalip(ip, initial_k_grid)

    smoothed_error = _approx_error(pk_ip, pk_tobe, width)
    pointwise_error = _approx_error(pk_ip, pk_tobe, 1)

    return kgrid, smoothed_error, pointwise_error


def _thinout(kgrid, pk_tobe, tolerance, width):
    k_full = kgrid.copy()
    pk_full = pk_tobe.copy()
    changed = True
    while changed:
        i = 1
        changed = False
        while i < len(kgrid) - 1:
            klocal = np.concatenate((kgrid[:i], kgrid[i + 1 :]))
            pk_local = np.concatenate((pk_tobe[:i], pk_tobe[i + 1 :]))
            ip = _buildip(klocal, pk_local)
            error = np.max(np.abs(_approx_error(_evalip(ip, k_full), pk_full, width)))
            i += 1
            if error < tolerance:
                # print("remove", kgrid[i], error)
                kgrid = klocal
                pk_tobe = pk_local
                changed = True
    return kgrid, pk_tobe


def _buildip(k, ps):
    if len(k) > 3:
        kind = "cubic"
    elif len(k) > 2:
        kind = "quadratic"
    else:
        kind = "linear"
    lnk = np.log(k)
    lnps = np.log(ps.flatten())
    ip0 = interp1d(lnk, lnps, kind=kind)
    return ip0


def _evalip(ip, k):
    return np.exp(ip(np.log(k)))


def _approx_error(pk_ip, pk_tobe, width):
    diff_smooth = convolve(
        np.abs(pk_ip / pk_tobe - 1.0), np.ones((width,)) / width, mode="same"
    )
    return np.max(np.abs(diff_smooth))
