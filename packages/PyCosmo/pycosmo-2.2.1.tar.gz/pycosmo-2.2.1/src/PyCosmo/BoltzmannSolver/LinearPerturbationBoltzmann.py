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

import itertools
import warnings
from functools import lru_cache
from multiprocessing import current_process

import numpy as np

from ..LinearPerturbationBase import LinearPerturbationBase
from .Fields import Fields
from .LsodaSolver import LsodaSolver


# use decorator to print messages only once per model:
@lru_cache(maxsize=1)
def print_new_traces(cache_file):
    print()
    print("new traces detected! you might want to run")
    print("recompile {}".format(cache_file))
    print()


proc_name = current_process().name


class LinearPerturbationBoltzmann(LinearPerturbationBase):
    """
    Class for computing linear perturbations by solving the Einstein-Boltzmann ODE
    system.

     The Boltzmann solver is selected using the *set function*:

        .. code-block:: python

            cosmo.set(pk_type = "boltz")

    """

    def __init__(self, cosmology):
        self._cosmo = cosmology
        self._params = cosmology.params
        self._background = cosmology.background
        self._solver = LsodaSolver(
            True,
            self._params.boltzmann_rtol,
            self._params.boltzmann_atol,
            self._params.boltzmann_max_bdf_order,
            self._params.boltzmann_max_iter,
            self._params.boltzmann_h0,
            self._cosmo,
            self._params.fast_solver,
        )
        self._wrapper = self._background._wrapper
        self._background = cosmology.background
        self._enrich_params()

    def _enrich_params(self):
        if self._params.pk_norm_type == "A_s":
            self._params.As_norm = self._params.pk_norm
        else:
            self._params.As_norm = None

    def _setup_norm(self):
        if self._params.As_norm is None and self._params.pk_norm_type == "sigma8":
            self._params.sigma8 = self._params.pk_norm
            self._params.As_norm = 2.0e-9  # arbitrary temporary value
            sigma8_temp = self.sigma8()
            self._params.As_norm = (
                self._params.As_norm * (self._params.sigma8 / sigma8_temp) ** 2
            )

    def max_redshift(self, k):
        """computes max redshift for which this model is applicable.
        uses the implemented initial conditions to determine this.

        :param k: wavenumber k [:math:`h Mpc^{-1}`]
        :returns: redshift
        """
        return 1 / (self.min_a(k) + 1.0)

    def min_a(self, k):
        return np.array([self._solver.initial_conditions(ki)[0] for ki in k])

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        """
        Returns the linear total matter power spectrum computed from the Boltzmann
        solver, this includes cold dark matter, baryons and massive neutrinos for an
        array of a and k values.

        :param a: scale factor [1] (default:a=1)
        :param k: wavenumber used to compute the power spectrum
                  (default:k=1 Mpc^1) [Mpc^-1]
        :param diag_only: if set to True: compute powerspectrum for pairs
                          :math:`a_i, k_i`, else consider all combinations
                          :math:`a_i, k_j`

        .. Warning ::
            If pk_norm_type = 'A_s' this will compute the total matter power spectrum
            following the general relativistic treatment (using delta_m_tot). If
            pk_norm_type = 'deltah' the Poisson equation will be assumed and the
            evolution will be split in growth factor and transfer function. We recommend
            the use of A_s or sigma8 normalizations.

        :return: P(a,k): total matter power spectrum [:math:`Mpc^3`]
        """
        a = np.atleast_1d(a)
        k = np.atleast_1d(k)

        min_a = self.min_a(k)

        if diag_only:
            assert len(a) == len(k)
            if any(ai < miai for (ai, miai) in zip(a, min_a)):
                warnings.warn(
                    f"some a values are below a={min_a:e} resp log_a={np.log(min_a):e}"
                    " for given k. invalid a values will be removed."
                )
            k = np.array([ki for (ki, ai, miai) in zip(k, a, min_a) if ai >= miai])

        else:
            min_a = np.max(min_a)
            if any(a < min_a):
                warnings.warn(
                    f"some a values are below a={min_a:e} resp log_a={np.log(min_a):e}"
                    " for given k. invalid a values will be removed."
                )

            # we need log to be compliant with the grid used internally
            a = a[np.log(a) > np.log(min_a)]

        if self._params.pk_norm_type == "deltah":
            warnings.warn(
                (
                    "We discourage the use of deltah normalization with the Boltzmann"
                    " solver!"
                ),
                UserWarning,
            )
            T_k = self.transfer_k(k=k)
            growth = self.growth_a(a, k=1)

            # using equation in section 2.4 of notes
            norm = (
                2.0
                * np.pi**2
                * self._params.pk_norm**2
                * (self._params.c / self._params.H0) ** (3.0 + self._params.n)
            )

            if diag_only:
                pk = norm * growth**2 * k**self._params.n * T_k**2
            else:
                # pk = norm * np.outer(growth.T ** 2, k ** self._params.n * T_k ** 2).T
                pk = norm * growth**2 * (k**self._params.n * T_k**2).reshape(-1, 1)

        if (self._params.pk_norm_type == "A_s") or (
            self._params.pk_norm_type == "sigma8"
        ):
            self._setup_norm()  # renormalization, links sigma8 and A_s
            pk = self._a_s_powerspec(a, k, diag_only)
            if diag_only:
                return pk.flatten()

        return pk

    def _a_s_powerspec(self, a, k, diag_only):
        norm = (
            2.0
            * np.pi**2
            * self._params.As_norm
            / self._params.k_pivot ** (self._params.n - 1)
        )

        kk = k / self._params.h
        src_m = np.zeros((len(a), len(k)))

        src_m = []

        if self._cosmo._pool is None:
            if diag_only:
                for ai, ki in zip(a, kk):
                    src_m.append(
                        src_m_column_j(
                            (
                                self._compute_fields_,
                                self._solver.solve,
                                self._cosmo._cache_file,
                                self._params,
                                self._background.H(ai),
                                self._wrapper,
                                ai,
                                ki,
                            )
                        )
                    )
            else:
                for ki in kk:
                    src_m.append(
                        src_m_column_j(
                            (
                                self._compute_fields_,
                                self._solver.solve,
                                self._cosmo._cache_file,
                                self._params,
                                self._background.H(a),
                                self._wrapper,
                                a,
                                ki,
                            )
                        )
                    )
        else:
            kk = np.array(kk)
            perm = np.argsort(kk)
            kk = kk[perm]
            src_m = [None] * len(kk)
            if diag_only:
                args = [
                    (
                        self._compute_fields_,
                        self._solver.solve,
                        self._cosmo._cache_file,
                        self._params,
                        self._background.H(ai),
                        self._wrapper,
                        ai,
                        ki,
                    )
                    for ai, ki in zip(a, kk)
                ]
            else:
                args = [
                    (
                        self._compute_fields_,
                        self._solver.solve,
                        self._cosmo._cache_file,
                        self._params,
                        self._background.H(a),
                        self._wrapper,
                        a,
                        ki,
                    )
                    for ki in kk
                ]

            src_m_cols = list(self._cosmo._pool.map(src_m_column_j, args))
            for i, pi in enumerate(perm):
                src_m[pi] = src_m_cols[i]

        src_m = np.vstack(src_m).T
        return norm * src_m.T**2 * k[:, None] ** (self._params.n - 4.0)

    def powerspec_cb_a_k(self, a=1.0, k=0.1, diag_only=False):
        """
        Returns the linear matter power spectrum of cold dark matter and baryons
        computed from the Boltzmann solver for an array of a and k values.


        :param a: scale factor [1] (default:a=1)
        :param k: wavenumber used to compute the power spectrum
                  (default:k=1 :math:`Mpc^{-1}`) [:math:`Mpc^{-1}`]
        :param diag_only: if set to True: compute powerspectrum for pairs
                        :math:`a_i, k_i`, else consider all combinations
                        :math:`a_i, k_j`

        :return: P_cb(a,k): power spectrum of CDM+baryons [:math:`Mpc^3`]
        """
        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        if diag_only:
            assert len(a) == len(k)

        if self._params.pk_norm_type == "deltah":
            raise ValueError("powerspec_cb_a_k is not supported for deltah normization")

        self._setup_norm()  # renormalization, links sigma8 and A_s

        norm = (
            2.0
            * np.pi**2
            * self._params.pk_norm
            / self._params.k_pivot ** (self._params.n - 1)
        )

        tk = np.zeros((len(a), len(k)))
        kk = k / self._params.h
        for j, onek in enumerate(kk):
            grid, y, meta, keep_lna0 = self._compute_fields(onek, grid=np.log(a))
            delta = y[:, 1]
            theta = y[:, 2] * onek
            delta_b = y[:, 3]
            theta_b = y[:, 4] * onek
            H = self._background.H(a) / (self._params.H0 * self._params.rh)
            delta_m_tot = self._params.omega_dm * delta + self._params.omega_b * delta_b
            theta_m_tot = self._params.omega_dm * theta + self._params.omega_b * theta_b

            tk[:, j] = (
                delta_m_tot + (3 * a * H / onek**2) * theta_m_tot
            ) / self._params.omega_m

        pk = norm * tk.T**2 * k[:, None] ** (self._params.n - 4.0)

        if diag_only:
            return np.diag(pk)

        return pk

    def growth_a(self, a=1.0, k=None):
        """
        Returns the linear growth factor computed from the Boltzmann solver at a given k
        value.

        :param a: scale factor [1]
        :param k: wavenumber used to compute the growth factor
                  (default:k=1 :math:`Mpc^{-1}`) [:math:`Mpc^{-1}`]

        :return: D(a): growth factor normalised to 1 at a=1 [1]
        """
        assert k is not None, (
            "growth factor of Einstein-Boltzmann model requires a k value"
        )
        # TODO: add option where D is normalised to a in matter dominated era
        grid = np.log(np.atleast_1d(a))
        if grid[-1] != 0.0:
            grid = np.append(grid, [0.0])

        grid, y, meta, keep_lna0 = self._compute_fields(k, grid=grid)
        delta = y[:, 1]
        growth = delta / delta[-1]

        # if a is a scalar, return a scalar
        if np.isscalar(a):
            return growth[0]
        # if a=1 is contained in a, return all values
        elif a[-1] == 1.0:
            return growth
        # remove the first value, since we added a=1
        else:
            return growth[:-1]

    def _transfer_k(self, args):
        try:
            i, k = args
            kk = np.atleast_1d(k) / self._params.h
            transfer = np.empty_like(kk)
            for index, onek in enumerate(kk):
                grid, y, meta, keep_lna0 = self._compute_fields(
                    onek, [0], keep_lna0=True
                )
                Phi = y[:, 0]
                transfer[index] = Phi[-1] / Phi[0]

            if np.isscalar(k):
                return transfer[0]
            else:
                return transfer
        except Exception:
            import traceback

            traceback.print_exc()
            raise

    def transfer_k(self, k):
        """
        Computes the linear matter transfer function using the Boltzmann solver
        assuming the Poisson equation.

        :param k:  wavenumber :math:`[ Mpc^{-1} ]`

        :return: Transfer function :math:`[ Mpc^{3/2} ]`
        """
        a_matter = np.sqrt(self._params.a_eq * self._params.a_eq2)
        corr_fac = self.growth_a(a_matter, k=1.0) / a_matter * 10.0 / 9.0

        if self._cosmo._pool is None or np.isscalar(k):
            return self._transfer_k((0, k)) * corr_fac

        pool = self._cosmo._pool

        k = np.array(k)
        n_chunks = min(len(k), pool._max_workers)

        perm = np.argsort(k)
        k = k[perm]
        args = [(i, k[i::n_chunks]) for i in range(n_chunks)]

        results = pool.map(self._transfer_k, args)
        # trick to revert chunking:
        unchunked = np.array(
            [ti for t in itertools.zip_longest(*results) for ti in t if ti is not None]
        )
        inverse_perm = np.arange(len(perm))[perm]
        return corr_fac * unchunked[inverse_perm]

    def fields(
        self,
        k,
        grid,
        sec_factor=5,
        keep_lna0=False,
        initial_conditions=None,
        enable_fast_solver=True,
        enable_sparse_lu_solver=True,
    ):
        """
        Solves the Einstein-Boltzmann ODE system for the evolution
        of the linear order perturbation of the fields.

        :param k: wavenumber :math:`[h/Mpc]`
        :param grid: ln(a) values at which to output fields [1]
        :param sec_factor: relaxes row permutation criterium in optimized LUP solver
        :param keep_lna0: if True includes the fields at initial time a_0
        :param initial_conditions: can pass a_0, y_0 (vector of initial conditions)
        :param enable_fast_solver: if set to False always use standard LUP solver for
                                   full matrix
        :param enable_sparse_lu_solver: if set to True: avoid iterating over known
                                        zero-entries in fallback LUP solver

        :return: Linear order perturbations, accessed with fields.a, fields.Phi etc.
        """
        grid, solver_result, meta, keep_lna_0 = self._compute_fields(
            k,
            grid,
            sec_factor,
            keep_lna0,
            initial_conditions,
            enable_fast_solver,
            enable_sparse_lu_solver,
        )
        fields = Fields(self._cosmo)
        fields.set_results(grid, solver_result)
        fields.meta = meta
        return fields

    def _sigma_k_grid(self):
        c = self._cosmo
        k_wiggles = np.pi / (c.background.r_s() / c.params.h)
        k_first = 10 ** np.linspace(-5, np.log10(k_wiggles), 10)

        h = np.pi / 5
        n = 22
        k_middle = k_wiggles * np.arange(1, n / h) * h

        k_last = 10 ** np.linspace(np.log10(k_middle[-1]), 2, 10)

        k_grid = np.hstack((k_first, k_middle, k_last))
        # remove duplicates in log values:
        return sorted({np.log(k): k for k in k_grid}.values())

    def _compute_fields(
        self,
        k,
        grid,
        sec_factor=3,
        keep_lna0=False,
        initial_conditions=None,
        enable_fast_solver=True,
        enable_sparse_lu_solver=True,
    ):
        return LinearPerturbationBoltzmann._compute_fields_(
            self._solver.solve,
            k,
            grid,
            sec_factor,
            keep_lna0,
            initial_conditions,
            enable_fast_solver,
            enable_sparse_lu_solver,
            self._cosmo._cache_file,
        )

    @staticmethod
    def _compute_fields_(
        solve,
        k,
        grid,
        sec_factor=3,
        keep_lna0=False,
        initial_conditions=None,
        enable_fast_solver=True,
        enable_sparse_lu_solver=True,
        cache_file=None,
    ):
        grid = np.atleast_1d(grid)
        grid, solver_result, meta = solve(
            k,
            grid,
            sec_factor,
            initial_conditions,
            enable_fast_solver,
            enable_sparse_lu_solver,
            keep_lna0,
        )
        new_traces = meta["new_traces"]
        if (isinstance(new_traces, dict) and new_traces) or (
            isinstance(new_traces, list) and any(new_traces)
        ):
            print_new_traces(cache_file)
        return grid, solver_result, meta, keep_lna0

    def P_R_k(self, k):
        """
        Computes the primordial power spectrum of gauge invariant curvature
        perturbations (R)

        :param k: wavenumber :math:`[1/Mpc]`
        :return: P_R(k), primordial power spectrum of R
        """
        if self._params.pk_norm_type == "A_s":
            norm = self._params.As_norm / self._params.k_pivot ** (self._params.n - 1)
        elif self._params.pk_norm_type == "sigma8":
            if self._params.As_norm is None:
                self._setup_norm()

            norm = self._params.As_norm / self._params.k_pivot ** (self._params.n - 1)
        else:
            raise ValueError("Need A_s or sigma8 normalization for P_R(k)")

        return norm * k ** (self._params.n - 1)


def src_m_column_j(args):
    compute_fields_, solve, cache_file, _params, H_, _wrapper, a, onek = args
    a = np.atleast_1d(a)
    grid, y, meta, keep_lna0 = compute_fields_(
        solve, onek, grid=np.log(a), cache_file=cache_file
    )

    n_grid = len(grid)
    a = a[-n_grid:]
    delta = y[:, 1]
    theta = y[:, 2] * onek
    delta_b = y[:, 3]
    theta_b = y[:, 4] * onek
    H = H_ / (_params.H0 * _params.rh)
    omega_nu_m = 0.0
    P_nu_m = 0.0
    omega_m_tot = _params.omega_m
    omega_plus_p_m_tot = _params.omega_m
    # include massive neutrinos in the total matter term
    src_col = np.zeros((n_grid,))
    if _params.N_massive_nu != 0:
        omega_nu_m = _wrapper.omega_nu_m_ufunc(a)
        P_nu_m = _wrapper.P_nu_m_ufunc(a)
        omega_m_tot += omega_nu_m / a
        omega_plus_p_m_tot += (omega_nu_m + P_nu_m) / a
        delta_nu_m = _wrapper.delta_nu_m_ufunc(a, y[1:])
        theta_nu_m = onek * _wrapper.u_nu_m_ufunc(a, y[1:])
        src_col += (
            delta_nu_m * omega_nu_m / a / omega_m_tot
            + (3 * a * H / onek**2)
            * theta_nu_m
            * (omega_nu_m + P_nu_m)
            / a
            / omega_plus_p_m_tot
        )

    delta_m_tot = _params.omega_dm * delta + _params.omega_b * delta_b
    theta_m_tot = _params.omega_dm * theta + _params.omega_b * theta_b

    src_col += (
        delta_m_tot / omega_m_tot
        + (3 * a * H / onek**2) * theta_m_tot / omega_plus_p_m_tot
    )
    return src_col
