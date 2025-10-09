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


import warnings

import numpy as np
from scipy.integrate import solve_ivp

from .Fields import Fields


class ScipySolver:
    _wrappers = {}

    def __init__(
        self,
        cosmology,
        method,
        **extra_args_for_solver,
    ):
        self.extra_args_for_solver = extra_args_for_solver

        self.params = cosmology.params
        self.cosmology = cosmology
        self.background = cosmology.background
        self.method = method

        self.wrapper = cosmology._wrapper

    def initial_conditions(self, k):
        self.wrapper.set_globals(k=k)

        initial_conditions = getattr(
            self.wrapper, "initial_values_" + self.params.initial_conditions, None
        )
        if initial_conditions is None:
            raise ValueError(
                "initial conditions '{}' not implemented.".format(
                    self.initial_conditions
                )
            )

        return initial_conditions()

    def _setup_globals(self, k):
        parameters = {"k": k}
        for key in self.wrapper.get_globals().keys():
            if key == "k":
                continue
            else:
                value = getattr(self.params, key)
            parameters[key] = value
        self.wrapper.set_globals(**parameters)
        return parameters

    def solve(
        self,
        k,
        grid,
    ):
        self._setup_globals(k)

        a_0, _, *y_0 = self.initial_conditions(k)
        lna0 = np.log(a_0)
        y_0 = np.array(y_0)

        if not isinstance(grid, float):
            grid = np.array(grid)

            if np.any(grid <= lna0):
                warnings.warn(
                    "grid starts before initial a0= {:e} resp lna0 = {:e}, removed"
                    " therefore gridpoints".format(a_0, lna0)
                )

            grid = grid[grid > lna0]
            grid = t_eval = np.concatenate(([lna0], grid))
            t_span = (min(grid), max(grid))
        else:
            assert grid > lna0
            t_eval = None
            t_span = (lna0, grid)

        def rhs(lna, y):
            return self.cosmology._wrapper.rhs_linear_perturbation(lna, y)

        def jac(lna, y):
            # transpose result to return array in fortran storage order:
            return np.ascontiguousarray(
                self.cosmology._wrapper.jac_linear_perturbation(lna, y).T
            )

        result = solve_ivp(
            rhs,
            t_span,
            y_0,
            self.method,
            t_eval=t_eval,
            jac=jac,
            **self.extra_args_for_solver,
        )

        meta = dict(result.items())
        assert meta["status"] == 0, meta
        y = meta.pop("y").T

        return grid, y, meta

    def fields(self, k, grid, keep_lna0=False):
        grid, y, meta = self.solve(k, grid)
        if not keep_lna0:
            grid = grid[1:]
            y = y[1:]

        fields = Fields(self.cosmology)
        fields.set_results(grid, y)
        fields.meta = meta
        return fields


class ScipySolverRSA(ScipySolver):
    def __init__(
        self,
        cosmology,
        method,
        **extra_args_for_solver,
    ):
        assert cosmology.model_config.main.model == "RSA", "please use RSA model"
        super().__init__(cosmology, method, **extra_args_for_solver)

    def solve(
        self,
        k,
        grid,
    ):
        self._setup_globals(k)

        a_0, _, *y_0 = self.initial_conditions(k)
        lna0 = np.log(a_0)
        y_0 = np.array(y_0)

        if not isinstance(grid, float):
            grid = np.array(grid)

            if np.any(grid <= lna0):
                warnings.warn(
                    "grid starts before initial a0= {:e} resp lna0 = {:e}, removed"
                    " therefore gridpoints".format(a_0, lna0)
                )

            grid = grid[grid > lna0]
            grid = t_eval = np.concatenate(([lna0], grid))
            t_span = (min(grid), max(grid))
        else:
            assert grid > lna0
            t_eval = None
            t_span = (lna0, grid)

        t_switch = switch_time(self.cosmology._wrapper)

        def jac(lna, y):
            j = self.cosmology._wrapper.linear_perturbation_jac(lna, y)
            n = int(np.sqrt(j.shape[0]))
            return j.reshape(n, n)

        def jac2(lna, y):
            return jac(lna, y)[:5, :5]

        if t_eval is None:
            t_before, t_after = None, None
        else:
            t_before = t_eval[t_eval <= t_switch]
            if t_before[-1] < t_switch:
                t_before = np.append(t_before, [t_switch])
            t_after = t_eval[t_switch <= t_eval]
            if t_after[0] > t_switch:
                t_after = np.append([t_switch], t_after)
        result = solve_ivp(
            self.cosmology._wrapper.ode_full_dot,
            (t_span[0], t_switch),
            y_0,
            self.method,
            t_eval=t_before,
            jac=jac,
            **self.extra_args_for_solver,
        )

        y0_rsa = result["y"][:5, -1]

        res2 = solve_ivp(
            self.cosmology._wrapper.rsa_dot,
            (t_switch, t_span[1]),
            y0_rsa,
            self.method,
            t_eval=t_after,
            jac=jac2,
            **self.extra_args_for_solver,
        )

        meta = dict(result.items())
        assert meta["status"] == 0, meta
        y1 = meta.pop("y").T
        y2 = np.array(res2.pop("y")).T
        tvec1 = result["t"]
        tvec2 = res2["t"]
        if t_eval is not None:
            if t_switch < t_eval[-1]:
                tvec1 = tvec1[:-1]
                y1 = y1[:-1]
            if t_switch not in t_eval and t_switch > t_eval[0]:
                tvec2 = tvec2[1:]
                y2 = y2[1:]

        y = merge(self.cosmology._wrapper, tvec1, t_switch, tvec2, y1, y2)

        meta = dict(
            status=max(meta["status"], res2["status"]),
            nfev=meta["nfev"] + res2["nfev"],
            nlu=meta["nlu"] + res2["nlu"],
            njev=meta["njev"] + res2["njev"],
            t=np.concatenate((tvec1, tvec2)),
        )

        return grid, y, meta

    def fields(self, k, grid, keep_lna0=False):
        grid, y, meta = self.solve(k, grid)
        if not keep_lna0:
            grid = grid[1:]
            y = y[1:]

        fields = Fields(self.cosmology)
        fields.set_results(grid, y)
        fields.meta = meta
        return fields


def merge(wrapper, t_0, t_switch, t_1, y_0, y_1):  # pragma: no cover
    """
    combine the non-RSA and RSA solutions
    and recompute the approximated radiation
    fields at output times
    """

    if len(t_1) == 0:
        return y_0

    # redefine needed params
    glob = wrapper.get_globals()
    k = glob["k"]
    H0 = glob["H0"]
    rh = glob["rh"]
    a = np.exp(t_1)

    Phi = y_1[:, 0]
    delta = y_1[:, 1]
    delta_b = y_1[:, 3]
    u_b = y_1[:, 4]

    omega_gamma = glob["omega_gamma"]
    omega_neu = glob["omega_neu"]
    omega_dm = glob["omega_dm"]
    omega_b = glob["omega_b"]

    H = wrapper.H_ufunc(np.exp(t_1))
    H_Mpc = H / H0 / rh  # [h Mpc^-1]

    # recompute fields with RSA
    N0_interp = Phi
    Theta0_interp = Phi + u_b * wrapper.taudot_interp_ufunc(a) / k

    dPhi_dlan = (
        -Phi
        - (k / (a * H_Mpc)) ** 2 / 3 * Phi
        + (1 / (rh * H_Mpc)) ** 2
        / 2
        * (
            (omega_dm * delta + omega_b * delta_b) * a**-3
            + 4 * (omega_gamma * Theta0_interp + omega_neu * N0_interp) * a**-4
        )
    )

    N1_interp = -2 * a * H_Mpc / k * dPhi_dlan
    Theta1_interp = (
        -2 * a * H_Mpc / k * dPhi_dlan
        + a
        * H_Mpc
        * wrapper.taudot_interp_ufunc(a)
        / k** 2
        * (
            u_b
            - k / (a * H_Mpc) * wrapper.c_s_interp_ufunc(a) ** 2 * delta_b
            + k / (a * H_Mpc) * Phi
        )
    )

    # reshape and stack perturbations
    N0_interp = np.reshape(N0_interp, (len(y_1[:, 0]), 1))
    Theta0_interp = np.reshape(Theta0_interp, (len(y_1[:, 0]), 1))
    N1_interp = np.reshape(N1_interp, (len(y_1[:, 0]), 1))
    Theta1_interp = np.reshape(Theta1_interp, (len(y_1[:, 0]), 1))
    ThetaP0_interp = np.zeros((len(y_1[:, 0]), 1))
    ThetaP1_interp = np.zeros((len(y_1[:, 0]), 1))

    y1_stacked = np.hstack(
        (
            y_1,
            Theta0_interp,
            ThetaP0_interp,
            N0_interp,
            Theta1_interp,
            ThetaP1_interp,
            N1_interp,
        )
    )
    y_1_complete = np.zeros((len(t_1), len(y_0[0, :])))
    y_1_complete[:, :11] = y1_stacked

    y = np.vstack((y_0, y_1_complete))

    return y


def switch_time(wrapper):  # pragma: no cover
    # use trigger parameters to determine a
    # at which RSA kicks in (as a function of k)
    a = np.logspace(-3, 0, 50)
    eta_ = wrapper.eta(a)
    a_tau = np.where(
        (
            -1 / (wrapper.taudot_interp_ufunc(a) * eta_)
            > wrapper.get_globals()["rsa_trigger_taudot_eta"]
        ),
        a,
        1.0,
    )
    lim = wrapper.get_globals()["k"] * eta_ > wrapper.get_globals()["rsa_trigger_k_eta"]
    a_keta = np.where(lim, a, 1.0)
    lna_cut = np.log(max(min(a_keta), min(a_tau)))
    return lna_cut
