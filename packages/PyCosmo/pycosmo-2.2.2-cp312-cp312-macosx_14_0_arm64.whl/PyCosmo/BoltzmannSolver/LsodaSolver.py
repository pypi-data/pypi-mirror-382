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


class LsodaSolver:
    SOLVER_ID = "linear_perturbation"

    _wrappers = {}

    def __init__(
        self,
        verbose,
        rtol,
        atol,
        max_bdf_order,
        max_iter,
        h0,
        cosmology,
        fast_solver,
        **extra_args_for_solver,
    ):
        self.verbose = verbose
        self.rtol = rtol
        self.atol = atol
        self.max_bdf_order = max_bdf_order
        self.max_iter = max_iter
        self.h0 = h0
        self.extra_args_for_solver = extra_args_for_solver

        self.params = cosmology.params
        # self.background = cosmology.background
        self.wrapper = cosmology._wrapper

        assert fast_solver, "slow solver not supported anymore"
        self.fast_solver = fast_solver

    def initial_conditions(self, k):
        self.wrapper.set_globals(k=k)

        initial_conditions = getattr(
            self.wrapper, "initial_values_" + self.params.initial_conditions, None
        )
        if initial_conditions is None:
            raise ValueError(
                "{}: initial conditions '{}' not implemented.".format(
                    self.wrapper, self.params.initial_conditions
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
        sec_factor=3,
        initial_conditions=None,
        enable_fast_solver=True,
        enable_sparse_lu_solver=True,
        keep_lna0=False,
    ):
        self._setup_globals(k)
        self.wrapper.set_sec_factor(sec_factor)

        if initial_conditions is not None:
            assert len(initial_conditions) == 2
            a_0, y_0 = initial_conditions
        else:
            a_0, _, *y_0 = self.initial_conditions(k)

        y_0 = np.array(y_0)
        lna0 = np.log(a_0)

        if np.any(grid <= lna0):
            warnings.warn(
                "grid starts before initial a0= {:e} resp lna0 = {:e}, removed"
                " therefore gridpoints".format(a_0, lna0)
            )
        grid = grid[grid > lna0]
        grid = np.concatenate(([lna0], grid))

        solver = getattr(self.wrapper, "solve_fast_" + self.SOLVER_ID)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            y, meta = solver(
                y_0,
                grid,
                self.rtol,
                self.atol,
                max_order=self.max_bdf_order,
                max_iter=self.max_iter,
                enable_fast_solver=enable_fast_solver,
                enable_sparse_lu_solver=enable_sparse_lu_solver,
                h0=self.h0,
            )
        if meta["istate"] <= 0:
            raise RuntimeError(f"solving ode failed for k = {k}, meta={meta}")

        start_idx = 0 if keep_lna0 else 1
        return grid[start_idx:], y[start_idx:], meta
