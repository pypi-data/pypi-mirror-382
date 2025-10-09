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


import numba
import numpy as np
import scipy.special

from PyCosmo.cython.halo_integral_1h import _integral_halo as cython_integral_halo_1h
from PyCosmo.cython.halo_integral_2h import _integral_halo as cython_integral_halo_2h
from PyCosmo.cython.rho_m_integral import _integral_halo as cython_integral_rho_m
from PyCosmo.PerturbationBase import NonLinearPerturbationBase
from PyCosmo.TheoryPredTables import TheoryPredTables

from ._scipy_utils import interp1d

"""
based on:

    Halo Model
    by Lukas Hergt, Institute for Astronomy, ETH Zurich


rewrite by:

    Uwe Schmitt
    Scientific IT Services
    ETH Zurich
    schmittu@ethz.ch
    March 2018

Edited by:

    Pascal Hitz
    Institute for Particle Physics and Astrophysics
    ETH Zurich
    hitzpa@phys.ethz.ch

"""


@numba.jit(numba.float64[:](numba.float64[:]), nopython=True)
def fft_top_hat(x):  # pragma: no cover
    """
    Fourier transform of 3D spherical top hat.

    :param x: Dimensionless parameter (usually k r)
    :return t: Fourier transform of a 3D spherical top hat.
    """

    cutoff = 1e-8
    # x values below thresh will yield a result abs smaller than cutoff:
    thresh = np.sqrt(6 / cutoff)

    t = np.zeros(len(x))

    for i, y in enumerate(x):
        if y > thresh:
            continue

        elif y > 1e-2:
            t[i] = 3.0 * (np.sin(y) - y * np.cos(y)) / y**3.0
        else:
            t[i] = 1.0 - y**2.0 / 10.0 + y**4.0 / 280.0

    return t


class NonLinearPerturbation_HaloModel(NonLinearPerturbationBase):
    r"""
    The class incorporates the implementation of the Halo Model.

    This can be set as:

        .. code-block:: python

            cosmo.set(pk_nonlin_type='HaloModel')

    .. Warning ::
        NonLinearPerturbation_HaloModel not supported by the Boltzmann solver yet.
        Calling any function from this module while using the Boltzmann solver
        (pk_type='boltz') will return
        **AttributeError: 'NoneType' object has no attribute 'function'**
    """

    def __init__(self, cosmo):
        self._model = cosmo.model_config
        self._params = cosmo.params
        self._background = cosmo.background
        self._lin_pert = cosmo.lin_pert
        self._tables = TheoryPredTables(self._lin_pert)

        self._enrich_params()
        self._setup_interpolation_functions()

    def _enrich_params(self):
        # Newton's gravitational constant as in Mo, Bosch & White, Galaxy Formation and
        # Evolution, 2010
        self._params.G_mead = 4.299e-9

        # Parameters used for the mass function, according to Sheth & Tormen, 2001 (ST),
        # Tinker et al., 2010 (Ti), or Watson et al., 2013 (Wa)
        if self._params.multiplicity_fnct == "ST":
            # Sheth & Tormen, 'Large scale bias and the peak background split', original
            # paper, 1999.
            # Explicit formula with A=0.3222 given in Sheth, Mo, & Tormen
            # 'Ellipsoidal collapse and an improved model for the number and spatial
            # distribution of dark matter haloes', 2001, eq. (6)
            self._params.mf_aa = 0.3222
            self._params.mf_a = 0.707
            self._params.mf_p = 0.3

        elif self._params.multiplicity_fnct == "Ti":
            # Tinker et al., 'Large-scale bias of dark matter halos', 2010, eq. (8)-(12)
            # Halo mass function parameters for Delta=200 are used.
            self._params.mf_aa = 0.368
            self._params.mf_a = -0.729
            self._params.mf_b = 0.589
            self._params.mf_c = 0.864
            self._params.mf_n = -0.243

        elif self._params.multiplicity_fnct == "Wa":
            # Watson et al., 'The halo mass function through the cosmic ages', 2013, eq.
            # (12)
            self._params.mf_aa = 0.282
            self._params.mf_a = 2.163
            self._params.mf_b = 1.406
            self._params.mf_c = 1.210

        self._params.rho_crit_Msun_iMpc3 = (
            3 * self._params.H0**2 / (8 * np.pi * self._params.G_mead)
        )
        self._params.rho_matter_Msun_iMpc3 = (
            self._params.rho_crit_Msun_iMpc3 * self._params.omega_m
        )

        self._params.bins = 1000

        # Parameters used for linear halo bias function, according to Sheth & Tormen
        # 1999 (ST), Sheth Mo & Tormen 2001 (SMT) or Tinker et al. 2010 (Ti)
        if self._params.lin_halo_bias_type == "ST":
            # Sheth and Tormen, 'Large scale bias and the peak background split', 1999,
            # eq. (12)
            self._params.hb_ST_a = 0.707
            self._params.hb_ST_p = 0.3

        elif self._params.lin_halo_bias_type == "SMT":
            # Sheth, Mo & Tormen, 'Ellipsoidal collapse and an improved model for the
            # number and
            # spatial distribution of dark matter haloes', 2001, eq. (8)
            self._params.hb_SMT_a = 0.707
            self._params.hb_SMT_b = 0.5
            self._params.hb_SMT_c = 0.6

        elif self._params.lin_halo_bias_type == "Ti":
            # Tinker et al., 'Large-scale bias of dark matter halos', 2010, eq. (6)
            # The halo bias parameters for Delta=200 are used
            self._params.hb_Ti_y = np.log10(200.0)
            self._params.hb_Ti_A = 1.0 + 0.24 * self._params.hb_Ti_y * np.exp(
                -((4.0 / self._params.hb_Ti_y) ** 4)
            )
            self._params.hb_Ti_a = 0.44 * self._params.hb_Ti_y - 0.88
            self._params.hb_Ti_B = 0.183
            self._params.hb_Ti_b = 1.5
            self._params.hb_Ti_C = (
                0.019
                + 0.107 * self._params.hb_Ti_y
                + 0.19 * np.exp(-((4.0 / self._params.hb_Ti_y) ** 4))
            )
            self._params.hb_Ti_c = 2.4

    def _setup_interpolation_functions(self, a0=0.5):
        r"""
        Set up derived parameters for scale factor :math:`a`. The order is slightly
        weird but this is due to the fact that the lookup tables need :math:`\delta_c`
        and n needs the lookup tables.

        :param a: Scale factor
        :param k: Wavenumber
        :return:
        """

        bins = self._params.bins
        assert bins >= 1000, "bins should be >=1000"

        m_grid = 10 ** np.linspace(-250, 20, bins - 1)
        s_grid_0 = self._sigma([m_grid], a0).flatten()

        assert np.all(np.diff(s_grid_0) <= 0), "s-array not monotone falling"

        self.sigma_a0_function = interp1d(
            np.log(m_grid + 1e-300),
            s_grid_0,
            kind="quadratic",
            fill_value="extrapolate",
        )

        if bins < 10000:
            m_vec = np.append([1e-300], 10 ** np.linspace(-250, 20, 9999))
            s_vec = self.sigma_a0_function(np.log(m_vec + 1e-300))
        else:
            m_vec = m_grid
            s_vec = s_grid_0

        self.delta_c_a0 = delta_c_a0 = self.delta_c(a0)
        self.nu0 = nu0 = delta_c_a0 / s_vec

        self.growth_a0 = self._tables.growth_tab_a(a=a0)

        self.nu0_to_mass = interp1d(nu0, m_vec, kind="linear", fill_value="extrapolate")

    def nu2mass(self, nu, a):
        r"""
        Extracts the halo mass from Eq.(17) in
        `Mead et al., 2015 <https://arxiv.org/abs/1505.07833>`_,
        :math:`\nu(M, a)=\delta_c / \sigma(M, a)`, by converting the :math:`\nu`-array
        into a mass-array by backwards interpolation.

        :param nu: Peak height :math:`\nu=\delta_c / \sigma(M, a)`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: Mass in solar masses :math:`[M_{\odot}]`
        """

        nu = np.atleast_1d(nu)
        a = np.atleast_1d(a)

        nu0 = nu * (self._tables.growth_tab_a(a=a) / self.growth_a0)[:, None]

        mask = nu0 < min(self.nu0)
        nu0[mask] = min(self.nu0)
        masses = self.nu0_to_mass(nu0)
        masses[mask] = 0
        return masses

    def delta_c(self, a):
        r"""
        Computation of the cosmology dependent linear collapse threshold,
        :math:`\delta_c`. For the mass functions of
        `Press & Schechter, 1974 <https://ui.adsabs.harvard.edu/abs/1974ApJ...187..425P/abstract>`_ ,
        `Sheth & Tormen, 1999 <https://arxiv.org/abs/astro-ph/9901122>`_ ,
        and `Watson et al., 2013 <https://arxiv.org/abs/1212.0095>`_ ,
        we use the cosmology dependent expression from
        `Nakamura & Suto, 1997 <https://arxiv.org/abs/astro-ph/9612074>`_ ,
        or `Mo & White, 2010 <https://doi.org/10.1017/CBO9780511807244>`_ .
        For the mass function of
        `Tinker et al., 2010 <https://arxiv.org/abs/1001.3162>`_ ,
        we assume :math:`\delta_c=1.686`.

        :param a: Scale factor, scalar or 1d array
        :return: Linear collapse threshold :math:`\delta_c`
        """

        a = np.atleast_1d(a)

        if self._params.multiplicity_fnct in ["PS", "ST", "Wa"]:
            if self._model["main"]["model"] == "LCDM" and self._params.flat_universe:
                fac = 3 * (12 * np.pi) ** (2 / 3) / 20
                dc = fac * (1.0 + 0.012299 * np.log10(self._background._omega_m_a(a=a)))
            elif self._model["main"]["model"] == "LCDM" and self._params.omega_l == 0.0:
                fac = 3 * (12 * np.pi) ** (2 / 3) / 20
                dc = fac * self._background._omega_m_a(a=a) ** 0.0185
            else:
                print("delta_c not defined for this cosmology.")
        elif self._params.multiplicity_fnct == "Ti":
            dc = np.ones_like(a) * 1.686

        return dc

    def mass2radius(self, m_msun):
        r"""
        Converts mass of a sphere in solar masses :math:`[M_{\odot}]` to the corresponding
        radius in :math:`[Mpc]`, assuming homogeneous density corresponding to the
        matter density of the universe at redshift :math:`z=0`.

        :param m_msun: Mass of sphere in solar masses :math:`[M_{\odot}]`, scalar or 1d array
        :return: Radius of the sphere in :math:`[Mpc]`
        """

        radius = (
            3.0 * m_msun / (4.0 * np.pi * self._params.rho_matter_Msun_iMpc3)
        ) ** (1.0 / 3.0)

        return radius

    def radius2mass(self, r_mpc):
        r"""
        Converts radius of a sphere in :math:`[Mpc]` to corresponding mass in solar
        masses :math:`[M_{\odot}]`, assuming homogeneous density corresponding to the matter
        density of the universe at redshift :math:`z=0`.

        :param r_mpc: Radius of sphere :math:`[Mpc]`, scalar or 1d array
        :return: Mass of sphere in solar masses :math:`[M_{\odot}]`
        """

        mass = 4.0 / 3.0 * np.pi * r_mpc**3.0 * self._params.rho_matter_Msun_iMpc3

        return mass

    def delta_vir(self, a):
        r"""
        Calculates the mean overdensity of a virialised dark matter halo for different
        cosmologies. We use equation (6) of `Bryan & Norman, 1998
        <https://arxiv.org/abs/astro-ph/9710107>`_ modified by a :math:`1/\Omega_m`
        term, because we work with respect to the matter density, rather than the
        critical density.

        :param a: Scale factor, scalar or 1d array
        :return: Mean overdensity of a dark matter halo :math:`\Delta_{vir}`
        """

        d_a = self._background._omega_m_a(a=a) - 1
        if self._model["main"]["model"] == "LCDM" and self._params.flat_universe:
            delta_vir = (
                18 * (np.pi**2) + 82 * d_a - 39 * (d_a**2)
            ) / self._background._omega_m_a(a=a)
        elif self._model["main"]["model"] == "LCDM" and self._params.omega_l == 0.0:
            delta_vir = (
                18 * (np.pi**2) + 60 * d_a - 32 * (d_a**2)
            ) / self._background._omega_m_a(a=a)

        return delta_vir

    def rvir(self, mvir_msun, a):
        # TODO: Extend this beyond flat cosmologies?
        r"""
        Calculates the virial radius corresponding to a dark matter halo of a given mass
        for different cosmologies.
        See `Bryan & Norman, 1998 <https://arxiv.org/abs/astro-ph/9710107>`_ for more
        details.

        :param mvir_msun: Halo mass in solar masses :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, 1d array
        :return: Virial radius in :math:`[Mpc]`
        """

        delta_v = self.delta_vir(a)

        rvir3 = (3.0 * mvir_msun) / (
            4.0 * np.pi * self._params.rho_matter_Msun_iMpc3 * delta_v[:, None]
        )

        rvir_mpc = rvir3 ** (1.0 / 3.0)

        return rvir_mpc

    def vvir(self, mvir_msun, a, diag_only=False):
        r"""
        Calculates the virial velocity corresponding to a dark matter halo of a given
        mass as described in
        `Barnes & Haehnelt, 2014 <https://arxiv.org/abs/1403.1873>`_ .

        :param mvir_msun: Halo mass in solar masses :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, 1d array
        :return: Virial velocity in :math:`[km/s]`
        """

        delta_v = self.delta_vir(a)

        if diag_only:
            vvir = 96.6 * (
                (delta_v * self._params.omega_m * (self._params.h**2) / 24.4) ** (1 / 6)
                * (a * 3.3) ** (-1 / 2)
                * (mvir_msun / 1e11) ** (1 / 3)
            )
        else:
            vvir = 96.6 * (
                (delta_v[:, None] * self._params.omega_m * (self._params.h**2) / 24.4)
                ** (1 / 6)
                * (a[:, None] * 3.3) ** (-1 / 2)
                * (mvir_msun / 1e11) ** (1 / 3)
            )

        return vvir

    def T(self, x):
        r"""
        Computes the Fourier Transform of a 3D spherical top-hat function.

        :param x: Dimensionless parameter (usually equal to :math:`kr`) [1]
        :return: Fourier Transform of a 3D spherical top-hat function
        """

        orig_shape = x.shape
        x_flat = np.ravel(x)
        t = fft_top_hat(x_flat)
        t = t.reshape(orig_shape)

        return t

    def sigma8_a(self, a):
        r"""
        Computes :math:`\sigma_8`, the RMS density contrast fluctuation, smoothed with a
        top hat of radius 8 :math:`h^{-1}Mpc` at scale factor :math:`a`.

        :param a: Scale factor, scalar or 1d array
        :return: :math:`\sigma_8` at the desired scale factor
        """

        a = np.atleast_1d(a)
        r = 8.0 / self._params.h  # smoothing radius [Mpc]
        k = np.logspace(-5.0, 2.0, num=5000)  # grid of wavenumber k [Mpc^-1]
        lnk = np.log(k)

        w = self.T(k * r)  # top hat window function
        pk = self._lin_pert.powerspec_a_k(a=a, k=k)
        res = np.trapezoid(k[:, None] ** 3 * pk * w[:, None] ** 2, lnk, axis=0)

        sig8z = np.sqrt(1.0 / (2.0 * np.pi**2) * res)
        return sig8z

    def _calc_sigma_integral(self, k, m_msun, a):
        r"""
        Calculates the unnormed :math:`\sigma^2`.

        :param k: Wavelength array over which the integration is performed
                  :math:`[Mpc^{-1}]`
        :param m_msun: Mass in solar masses at which :math:`\sigma^2` is
                       evaluated :math:`[M_{\odot}]`
        :param a: Scale factor
        :return: Unnormed :math:`\sigma^2` [dimensionless]
        """

        # here: first dimension: k, second msun, third a

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)
        m_msun = np.atleast_2d(m_msun)

        nk = k.shape[0]
        na = a.shape[0]
        nm = m_msun.shape[1]
        assert m_msun.shape[0] == na

        ps = self._lin_pert.powerspec_a_k(a=a, k=k)[:, None, :]

        r_mpc = np.atleast_2d(self.mass2radius(m_msun=m_msun)).T[None, :, :]
        assert r_mpc.shape == (1, nm, na)

        t = self.T(x=r_mpc * k[:, None, None])
        assert t.shape == (nk, nm, na)
        integrand_mpc = ps * t**2.0 * k[:, None, None] ** 3.0

        integral = np.trapezoid(integrand_mpc, np.log(k), axis=0)

        return integral.flatten()

    def _sigma(self, m_msun, a):
        r"""
        Computes :math:`\sigma` for a single :math:`a`.

        :param m_msun: Mass in solar masses :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, scalar
        :return: :math:`\sigma`
        """

        a = np.atleast_1d(a)
        assert len(a) == 1

        nk = self._params.npoints_k
        # Wavenumber k [Mpc^1] to integrate over
        k = np.append([1e-100], 10 ** np.linspace(-10, 100, nk))
        # This deals with missing factors of 2 pi^2 - could also be omitted!
        m_msun_8 = self.radius2mass(8.0 / self._params.h)
        sigma8norm = np.sqrt(self._calc_sigma_integral(k=k, m_msun=m_msun_8, a=a))

        # We need to normalise with the value of sigma8 at the desired redshift
        s8z = self.sigma8_a(a=a)
        sigma = np.sqrt(self._calc_sigma_integral(k=k, m_msun=m_msun, a=a))

        return sigma / sigma8norm * s8z

    # sigma -> _sigma_m_a, can I move this to HaloFitBaseClass API ?

    def sigma(self, m_msun, a):
        r"""
        Calculates :math:`\sigma(M, a)`, the RMS of the density field at a given mass.

        :param m_msun: Mass in solar masses at which :math:`\sigma` is evaluated
                       :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: :math:`\sigma(M, a)` as the RMS of the density field
        """

        a = np.atleast_1d(a)
        m_msun = np.atleast_1d(m_msun)
        if m_msun.ndim == 1:
            m_msun = np.atleast_2d([m_msun] * len(a))
        assert m_msun.shape[0] == a.shape[0]

        # we make use of the fact that sigma(a) / growth(a) == sigma(a') / growth(a').
        # so for a particular m_msun and a vector a we only need to compute sigma for
        # the first entry of a, and all other sigma values can be computed by scaling.
        sigma0s = []
        for ai, msi in zip(a, m_msun):
            sigma0 = self.sigma_a0_function(np.log(msi + 1e-300)) / self.growth_a0
            sigma0s.append(sigma0)
        growth_a = self._tables.growth_tab_a(a=a)
        return (growth_a[:, None] * np.vstack(sigma0s)).T

    def f(self, nu, a=1.0):
        r"""
        Multiplicity function :math:`f(\nu, a)` as it appears in the calculation of the
        Halo Mass Function. The available fitting functions are
        `Press & Schechter ('PS'), 1974 <https://ui.adsabs.harvard.edu/abs/1974ApJ...187..425P/abstract>`_,
        `Sheth & Tormen ('ST'), 1999 <https://arxiv.org/abs/astro-ph/9901122>`_ ,
        `Tinker et al. ('Ti'), 2010 <https://arxiv.org/abs/1001.3162>`_ ,
        and `Watson et al. ('Wa'), 2013 <https://arxiv.org/abs/1212.0095>`_ .

        :param nu: Peak height :math:`\nu=\delta_c / \sigma(M, a)`, scalar or 1d array
        :param a: Scale factor, a=1.0 for multiplicity function='PS', 'ST', and 'Wa',
                  scalar or 1d array for 'Ti'
        :return: Multiplicity function :math:`f(\nu, a)`

        Example of setting the multiplicity function:

        .. code-block:: python

            cosmo.set(multiplicity_fnct=option)

        where *option* can be 'PS' for *Press & Schechter (1974)*, 'ST' for *Sheth &
        Tormen (1999)*, 'Ti' for *Tinker et al., 2010*, or 'Wa' for *Watson et al., 2013*.
        """

        if self._params.multiplicity_fnct == "PS":
            # Press & Schechter, 'Formation of Galaxies and Clusters of Galaxies by
            # self-similar gravitational condensation' (1974)
            f = np.sqrt(2.0 / np.pi) * np.exp(-(nu**2.0) / 2.0)

        elif self._params.multiplicity_fnct == "ST":
            # Sheth & Tormen, 'Large scale bias and the peak background split', original
            # paper, 1999. Explicit formula with A=0.3222 given in Sheth, Mo, & Tormen
            # 'Ellipsoidal collapse and an improved model for the number and spatial
            # distribution of dark matter haloes', 2001, eq. (6)
            f = (
                self._params.mf_aa
                * np.sqrt(2.0 * self._params.mf_a / np.pi)
                * (1.0 + (self._params.mf_a * nu**2.0) ** (-self._params.mf_p))
                * np.exp(-self._params.mf_a * nu**2.0 / 2.0)
            )

        elif self._params.multiplicity_fnct == "Ti":
            # Tinker et al., 'Large-scale bias of dark matter halos', 2010, eq. (8)-(12)
            # Halo mass function parameters for Delta=200 are used.
            a = np.where(a > 1 / (1 + 3.0), a, 1 / (1 + 3.0))
            if np.size(a) > 1:
                a = a[:, None]

            mf_b_a = self._params.mf_b * a ** (-0.20)
            mf_a_a = self._params.mf_a * a**0.08
            mf_n_a = self._params.mf_n * a ** (-0.27)
            mf_c_a = self._params.mf_c * a**0.01

            f = (
                self._params.mf_aa
                * (1.0 + (mf_b_a * nu) ** (-2.0 * mf_a_a))
                * nu ** (2.0 * mf_n_a)
                * np.exp(-mf_c_a * nu**2.0 / 2)
            )

        elif self._params.multiplicity_fnct == "Wa":
            # Watson et al., 'The halo mass function through the cosmic ages', 2013, eq.
            # (12)
            sigma = self.delta_c(a=1.0) / nu
            f = (
                self._params.mf_aa
                * (1.0 + (self._params.mf_b / sigma) ** (self._params.mf_a))
                * np.exp(-self._params.mf_c / (sigma**2.0))
                / nu
            )

        else:
            raise NotImplementedError(
                "{} for multiplicity_fit in calc_f is not supported, use one of "
                "the following options: 'PS' for Press & Schechter, 'ST' for "
                "Sheth & Tormen, 'Ti' for Tinker et al., "
                "or 'Wa' for Watson et al.".format(self._params.multiplicity_fnct)
            )
        return f

    def mass2nu(self, m_msun, a):
        r"""
        Calculates the peak height :math:`\nu(M, a)=\delta_c / \sigma(M, a)` as a
        function of the halo mass and scale factor.

        :param m_msun: Halo mass :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return nu: Peak height
        """

        delta_c = self.delta_c(a)
        a_1 = np.atleast_1d(a)
        if len(a_1) == 1:
            sigma = self._sigma(m_msun, a_1)  # for a_1 a scalar or 1d array only
        else:
            sigma = self.sigma(m_msun, a_1)
        nu = delta_c / sigma
        return nu.T

    def _dnu_dm_of_m(self, m_msun, a, dm=1.0e5):
        r"""
        Calculates :math:`\frac{d\nu}{dM}` as a function of the halo mass.

        :param m_msun: Halo mass :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :param dm: Accuracy for triangle approximation of derivative :math:`[M_{\odot}]`, scalar
        :return dnu_dm: :math:`\frac{d\nu}{dM}` as used for halo mass function
        """

        if np.any(np.isnan(self.mass2nu(m_msun - dm / 2.0, a))):
            print(
                r"Minimal nu is too small, dnu/dm not defined for some nu. Choose"
                " higher minimal nu or smaller dm!"
            )

        dnu = self.mass2nu(m_msun + dm / 2.0, a) - self.mass2nu(m_msun - dm / 2.0, a)
        dnu_dm = dnu / dm
        return dnu_dm

    def dn_dm_of_m(self, m_msun, a, dm=1.0e5):
        r"""
        Calculates mass function :math:`\frac{dn}{dM}`
        as a function of the halo mass.
        The functional form depends on the selected multiplicity function
        :math:`f(\nu, a)`, see the corresponding documentation.

        :param m_msun: Halo mass :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :param dm: Accuracy for triangle approximation of derivative :math:`[M_{\odot}]`,
                   scalar
        :return dn_dm: Mass function :math:`\frac{dn}{dM}` :math:`[M_{\odot}^{-1} Mpc^{-3}]`
        """

        a = np.atleast_1d(a)
        m_msun = np.atleast_1d(m_msun)

        dens = self._params.rho_matter_Msun_iMpc3
        nu = self.mass2nu(m_msun, a)
        mult_func = self.f(nu=nu, a=a)
        dnu_dm = self._dnu_dm_of_m(m_msun, a, dm)
        dn_dm = dens * dnu_dm * mult_func / m_msun
        return dn_dm

    def subhalos_dn_dm_of_m(
        self,
        subhalo_m_msun,
        mean_subhalo_mass_fraction=0.5,
        host_halo_mass_msun=1e12,
        beta=0.3,
        gamma=0.9,
    ):
        r"""
        Compute subhalo mass function as a function of subhalo masses and host halo mass.

        References:
            Chapter 7.5 of Mo, van den Bosch and White (Equations 7.149 and 7.150)
            Left panel of Figure 2 from
            `Jiang et al., 2017 <https://arxiv.org/abs/1610.02399>`_
            informs the value for mean_subhalo_mass_fraction ~ 0.1

        Recommended values:
            mean_subhalo_mass_fraction: By definition, between 0 and 1.
                                        Default=0.1, informed by arxiv:1610.02399

            beta ~ 0.1 - 0.5, always < 1 (according to Mo, van den Bosch and White)

            gamma ~ 0.8 - 1.0 (according to Mo, van den Bosch and White)

        :param subhalo_m_msun: Subhalo mass :math:`[M_{\odot}]`, scalar or 1d array
        :param mean_subhalo_mass_fraction: Mean mass fraction contained in subhalos,
                                           scalar
        :param host_halo_mass_msun: Mass of the host halo for which this subhalo mass
                                    function is computed :math:`[M_{\odot}]`, scalar
        :param beta: Exponent, scalar
        :return dn_dm: Subhalo mass function
                       :math:`\frac{dn}{dM}` :math:`[M_{\odot}^{-1} Mpc^{-3}]`
        """

        # Validate data types and reasonable values for mass function parameters
        assert isinstance(mean_subhalo_mass_fraction, float)
        assert isinstance(beta, float)
        assert isinstance(gamma, float)
        assert beta > 0
        assert beta < 1
        assert mean_subhalo_mass_fraction > 0
        assert mean_subhalo_mass_fraction < 1

        subhalo_m_msun = np.atleast_1d(subhalo_m_msun)

        # Compute subhalo mass function according to book reference
        normalization = mean_subhalo_mass_fraction / (
            beta * scipy.special.gamma(1 - gamma)
        )
        factor = subhalo_m_msun / (beta * host_halo_mass_msun)
        power_law_value = np.power(factor, -gamma)
        exponential_value = np.exp(-factor)

        dn_dlnm = normalization * power_law_value * exponential_value

        dn_dm = dn_dlnm / subhalo_m_msun

        return dn_dm

    def dn_dlnm_of_m(self, m_msun, a, dm=1.0e5):
        r"""
        Calculates the logarithmic mass function :math:`\frac{dn}{dln M}`
        as a function of the halo mass.
        The functional form depends on the selected multiplicity function
        :math:`f(\nu, a)`, see the corresponding documentation.

        :param m_msun: Halo mass :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :param dm: Accuracy for triangle approximation of derivative
                   :math:`[M_{\odot}]`, scalar
        :return dn_dlnm: Logarithmic mass function :math:`\frac{dn}{d\ln M}`
                         :math:`[Mpc^{-3}]`
        """

        a = np.atleast_1d(a)
        m_msun = np.atleast_1d(m_msun)

        dn_dlnm = self.dn_dm_of_m(m_msun, a, dm) * m_msun

        return dn_dlnm

    def dn_dlogm_of_m(self, m_msun, a, dm=1.0e5):
        r"""
        Calculates logarithmic mass function :math:`\frac{dn}{d\log_{10} M}`
        as a function of the halo mass.
        The functional form depends on the selected multiplicity function
        :math:`f(\nu, a)`, see the corresponding documentation.

        :param m_msun: Halo mass :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :param dm: Accuracy for triangle approximation of derivative :math:`[M_{\odot}]`,
                   scalar
        :return dn_dlogm: Logarithmic mass function
                          :math:`\frac{dn}{d\log_{10} M}` :math:`[Mpc^{-3}]`
        """

        a = np.atleast_1d(a)
        m_msun = np.atleast_1d(m_msun)

        dn_dlogm = self.dn_dm_of_m(m_msun, a, dm) * m_msun * np.log(10.0)

        return dn_dlogm

    def dn_dm_of_nu(self, nu, a, dm=1.0e5):
        r"""
        Calculates mass function :math:`\frac{dn}{dM}`
        as a function of the peak height :math:`\nu=\delta_c / \sigma(M, a)`.
        The functional form depends on the selected multiplicity function
        :math:`f(\nu, a)`, see the corresponding documentation.

        :param nu: Peak height :math:`\nu=\delta_c / \sigma(M, a)`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :param dm: Accuracy for triangle approximation of derivative :math:`[M_{\odot}]`,
                   scalar
        :return dn_dm: Mass function :math:`\frac{dn}{dM}` :math:`[M_{\odot}^{-1} Mpc^{-3}]`
        """

        a = np.atleast_1d(a)
        nu = np.atleast_1d(nu)

        dens = self._params.rho_matter_Msun_iMpc3
        mult_func = self.f(nu=nu, a=a)
        m_msun = self.nu2mass(nu, a)
        dnu_dm = self._dnu_dm_of_m(m_msun, a, dm)
        dn_dm = np.ndarray.flatten(dens * dnu_dm * mult_func / m_msun)
        dn_dm = np.reshape(dn_dm, (len(a), len(nu)))

        return dn_dm

    def dn_dlnm_of_nu(self, nu, a, dm=1.0e5):
        r"""
        Calculates logarithmic mass function :math:`\frac{dn}{d\ln M}`
        as a function of the peak height :math:`\nu=\delta_c / \sigma(M, a)`.
        The functional form depends on the selected multiplicity function
        :math:`f(\nu, a)`, see the corresponding documentation.

        :param nu: Peak height :math:`\nu=\delta_c / \sigma(M, a)`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :param dm: Accuracy for triangle approximation of derivative :math:`[M_{\odot}]`,
                   scalar
        :return dn_dlnm: Logarithmic mass function :math:`\frac{dn}{d\ln M}`
                         :math:`[Mpc^{-3}]`
        """

        a = np.atleast_1d(a)
        nu = np.atleast_1d(nu)

        m_msun = self.nu2mass(nu, a)
        dn_dlnm = np.ndarray.flatten(self.dn_dm_of_m(m_msun, a, dm) * m_msun)
        dn_dlnm = np.reshape(dn_dlnm, (len(a), len(nu)))

        return dn_dlnm

    def dn_dlogm_of_nu(self, nu, a, dm=1.0e5):
        r"""
        Calculates logarithmic mass function :math:`\frac{dn}{d\log_{10} M}`
        as a function of the peak height :math:`\nu=\delta_c / \sigma(M, a)`.
        The functional form depends on the selected multiplicity function
        :math:`f(\nu, a)`, see the corresponding documentation.

        :param nu: Peak height :math:`\nu=\delta_c / \sigma(M, a)`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :param dm: Accuracy for triangle approximation of derivative :math:`[M_{\odot}]`,
                   scalar
        :return dn_dlogm: Logarithmic mass function :math:`\frac{dn}{d\log_{10} M}`
                          :math:`[Mpc^{-3}]`
        """

        a = np.atleast_1d(a)
        nu = np.atleast_1d(nu)

        m_msun = self.nu2mass(nu, a)
        dn_dlogm = np.ndarray.flatten(
            self.dn_dm_of_m(m_msun, a, dm) * m_msun * np.log(10.0)
        )
        dn_dlogm = np.reshape(dn_dlogm, (len(a), len(nu)))

        return dn_dlogm

    def cm(self, m_msun, a):
        r"""
        *Concentration-mass* function of dark matter haloes. The implemented fitting
        function is from `Bullock et al., 2001 <https://arxiv.org/abs/astro-ph/9908159>`_.

        :param m_msun: Halo mass in solar masses :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor a, scalar or 1d array
        :return: Concentration :math:`c(M, a)` of a halo mass :math:`[M_{\odot}]` at scale
                 factor :math:`a`
        """

        a = np.atleast_1d(a)
        z = 1.0 / a - 1.0

        if self._params.w0 != -1:
            raise NotImplementedError(
                "{} for concentration-mass relation is not supported for w!=-1"
            )

        # Bullock et al., 'Profiles of dark haloes: evolution, scatter and environment',
        # 2001 The correction by Dolag is not required

        # Determine the linear growth factor at the formation scale factor as in Eq.
        # (15) of Mead et al., 2015 It is used to calculate the formation scale factor
        # below
        gzf = (
            self.delta_c(a)
            / self.sigma(0.01 * m_msun, a)
            * self._tables.growth_tab_a(a=a)
        )

        # Determine the formation redshift
        af = self._tables.inv_growth_tab_a(g=gzf)
        zf = 1.0 / af - 1.0

        c = 4.0 * (1.0 + zf) / (1.0 + z)
        # If the formation redshift is smaller than z i.e. in the future we set c=A
        c[zf < z] = 4.0

        return c.T

    def lin_halo_bias_of_nu(self, nu, a):
        r"""
        Calculates the linear halo bias for a given peak height :math:`\nu=\delta_c / \sigma(M, a)`.
        The available biases are
        `Mo & White ('MW'), 1996 <https://arxiv.org/abs/astro-ph/9512127>`_ ,
        `Sheth & Tormen ('ST'), 1999 <https://arxiv.org/abs/astro-ph/9901122>`_ ,
        `Sheth, Mo & Tormen ('SMT'), 2001 <https://arxiv.org/abs/astro-ph/9907024>`_ ,
        and `Tinker et al. ('Ti'), 2010 <https://arxiv.org/abs/1001.3162>`_ .

        :param nu: Peak height :math:`\nu=\delta_c / \sigma(M, a)`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return lin_halo_bias: Linear halo bias

        Example of setting the linear halo bias:

        .. code-block:: python

            cosmo.set(lin_halo_bias_type=option)

        where *option* can be 'MW' for *Mo & White (1996)*, 'ST' for *Sheth &
        Tormen (1999)*, 'SMT' for *Sheth, Mo & Tormen (2001)*, or 'Ti'
        for *Tinker et al., 2010*.
        """

        delta_c = self.delta_c(a)[:, None]

        if self._params.lin_halo_bias_type == "MW":
            # Mo & White, 'An analytic model for the spatial clustering of dark matter
            # haloes' (1996)
            lin_halo_bias = 1.0 + (nu**2 - 1.0) / delta_c

            return lin_halo_bias

        elif self._params.lin_halo_bias_type == "ST":
            # Sheth & Tormen, 'Large scale bias and the peak background split' (1999),
            # eq. (12)
            term1 = (self._params.hb_ST_a * nu**2 - 1) / delta_c
            term2 = (
                2
                * self._params.hb_ST_p
                / (
                    delta_c
                    * (1 + (self._params.hb_ST_a * nu**2) ** self._params.hb_ST_p)
                )
            )
            lin_halo_bias = 1 + term1 + term2
            return lin_halo_bias

        elif self._params.lin_halo_bias_type == "SMT":
            # Sheth, Mo & Tormen, 'Ellipsoidal collapse and an improved model for the
            # number and spatial distribution of dark matter haloes' (2001)
            sum_1 = np.sqrt(self._params.hb_SMT_a) * self._params.hb_SMT_a * nu**2
            sum_2 = (
                np.sqrt(self._params.hb_SMT_a)
                * self._params.hb_SMT_b
                * (self._params.hb_SMT_a * nu**2) ** (1 - self._params.hb_SMT_c)
            )
            a_nu2_toc = (
                self._params.hb_SMT_a * nu**2
            ) ** self._params.hb_SMT_c  # for abbreviation
            sum_3 = (
                -1.0
                * a_nu2_toc
                / (
                    a_nu2_toc
                    + self._params.hb_SMT_b
                    * (1 - self._params.hb_SMT_c)
                    * (1 - self._params.hb_SMT_c / 2.0)
                )
            )
            lin_halo_bias = 1.0 + (sum_1 + sum_2 + sum_3) / (
                np.sqrt(self._params.hb_SMT_a) * delta_c
            )
            return lin_halo_bias

        elif self._params.lin_halo_bias_type == "Ti":
            # Tinker et al., 'The Large Scale Bias of Dark Matter Halos: Numerical
            # Calibration and Model Tests' (2010). Linear halo bias fit for Delta=200
            # is used.
            lin_halo_bias = (
                1.0
                - self._params.hb_Ti_A
                * (nu**self._params.hb_Ti_a)
                / (nu**self._params.hb_Ti_a + delta_c**self._params.hb_Ti_a)
                + self._params.hb_Ti_B * nu**self._params.hb_Ti_b
                + self._params.hb_Ti_C * nu**self._params.hb_Ti_c
            )
            return lin_halo_bias

        else:
            raise NotImplementedError(
                "{} for lin_halo_bias_type is not supported, use one of "
                "the following options: 'Ti' for Tinker et al. 2010, "
                "'SMT' for Sheth, Mo & Tormen 2001, "
                "'ST' for Sheth & Tormen 1999,"
                "or 'MW' for Mo & White 1996".format(self._params.multiplicity_fnct)
            )

    def max_redshift(self, k):
        r"""
        Computes max redshift for which this model is applicable.

        :param k: Wavenumber k, might be needed for some underlying linear perturbation
                  models. :math:`[h Mpc^{-1}]`
        :returns: Redshift
        """

        return self._lin_pert.max_redshift(k)

    def rho_m(self, a):
        r"""
        Calculates the mean dark matter density as a function of the scale factor.

        :param a: Scale factor, scalar or 1d array
        :return: Mean matter density, in :math:`[M_{\odot} \ Mpc^{-3}]`

        Example of setting the multiplicity function and the assumed minimal and maximal
        halo masses in solar masses :math:`[M_{\odot}]` considered in the calculation:

        .. code-block:: python

            cosmo.set(multiplicity_fnct=option,
                      min_halo_mass=1e8,
                      max_halo_mass=1e14)

        where *option* can be 'PS' for *Press & Schechter (1974)*, 'ST' for *Sheth &
        Tormen (1999)*, 'Ti' for *Tinker et al., 2010*, or 'Wa' for
        *Watson et al., 2013*.
        Default values for the minimal and maximal halo masses are
        min_halo_mass=1 and max_halo_mass=1e+20.
        """

        a = np.atleast_1d(a).astype(float)
        k = 0.1
        k = np.atleast_1d(k).astype(float)

        a_limit = 1 / (1 + self.max_redshift(k))
        mask_invalid = (a <= a_limit) | (a > 1.0)
        a[mask_invalid] = a_limit

        int_steps = 2000
        m_msun = np.logspace(
            np.log10(self._params.min_halo_mass),
            np.log10(self._params.max_halo_mass),
            int_steps,
        )

        nu_range = self.mass2nu(m_msun=m_msun, a=a)
        nu_range = np.atleast_2d(nu_range)

        f = self.f(nu=nu_range, a=a)

        # adapting the multiplicity function to satisfy the normalization condition
        # corrections to the first mass bin that is used corrections such that int(f
        # dnu)=1. But just if we integrate below one solar mass.
        if self._params.min_halo_mass <= 1.0:
            delta_nu = nu_range[:, 1] - nu_range[:, 0]
            diff_f = 1 - np.trapezoid(f, nu_range)
            const_f = diff_f / delta_nu * 2.0
            f[:, 0] += const_f

        integral_rho_m = cython_integral_rho_m(k, m_msun, nu_range, a, f, adaptive=1)
        rho_m_total = integral_rho_m * self._params.rho_matter_Msun_iMpc3

        return rho_m_total

    def pk_1h(self, k, a):
        r"""
        One-Halo term :math:`P_\text{1h}(k, a)` of the non-linear matter power spectrum as
        described in Eq. (7.191) of Mo et al. "Galaxy Formation and Evolution" (2010).

        :param k: Wavelength :math:`[Mpc^{-1}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: One-Halo power spectrum :math:`P_\text{1h}(k, a) \ [Mpc^{3}]`

        Example of setting the multiplicity function, linear halo bias, halo profile,
        and the assumed minimal and maximal halo masses in solar masses :math:`[M_{\odot}]`
        considered in the calculation:

        .. code-block:: python

            cosmo.set(multiplicity_fnct=option_mf,
                      lin_halo_bias_type=option_b,s
                      halo_profile=option_p,
                      min_halo_mass=1e8, max_halo_mass=1e14)

        where the possible *option_mf* are given in the documentation to
        :math:`f(\nu, a)`, *option_b* in the documentation to the linear halo bias
        and *option_p* is either True for a NFW-profile or False for assumed point
        sources.
        Default values for the minimal and maximal halo masses are
        min_halo_mass=1 and max_halo_mass=1e+20.
        """

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)

        int_steps = 2000
        m_msun = np.logspace(
            np.log10(self._params.min_halo_mass),
            np.log10(self._params.max_halo_mass),
            int_steps,
        )

        nu_range = self.mass2nu(m_msun=m_msun, a=a)
        nu_range = np.atleast_2d(nu_range)

        rv_mpc = self.rvir(m_msun, a)
        rv_mpc = np.atleast_2d(rv_mpc)

        c = self.cm(m_msun, a)
        c = np.atleast_2d(c)

        f = self.f(nu=nu_range, a=a)

        # adapting the multiplicity function to satisfy the normalization condition
        # corrections to the first mass bin that is used corrections such that int(f
        # dnu)=1. But just for if we integrate below one solar mass.
        if self._params.min_halo_mass <= 1.0:
            delta_nu = nu_range[:, 1] - nu_range[:, 0]
            diff_f = 1 - np.trapezoid(f, nu_range)
            const_f = diff_f / delta_nu * 2.0
            f[:, 0] += const_f

        integral_1halo = cython_integral_halo_1h(
            k, m_msun, nu_range, rv_mpc, c, a, f, self._params.halo_profile, adaptive=1
        )

        rho_m = self.rho_m(a)

        pk_1h = integral_1halo * self._params.rho_matter_Msun_iMpc3 / rho_m**2

        return pk_1h

    def pk_2h(self, k, a):
        r"""
        Two-Halo term :math:`P_\text{2h}(k, a)` of the non-linear matter power spectrum as
        described in Eq. (7.194) of Mo et al. "Galaxy Formation and Evolution" (2010).

        :param k: Wavelength :math:`[Mpc^{-1}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: Two-Halo power spectrum :math:`P_\text{2h}(k, a) \ [Mpc^{3}]`

        Example of setting the multiplicity function, linear halo bias, halo profile,
        and the assumed minimal and maximal halo masses in solar masses :math:`[M_{\odot}]`
        considered in the calculation:

        .. code-block:: python

            cosmo.set(multiplicity_fnct=option_mf,
                      lin_halo_bias_type=option_b,
                      halo_profile=option_p,
                      min_halo_mass=1e8,
                      max_halo_mass=1e14)

        where the possible *option_mf* are given in the documentation to :math:`f(\nu, a)`,
        *option_b* in the documentation to the linear halo bias
        and *option_p* is either True for a NFW-profile or False for assumed point sources.
        Default values for the minimal and maximal halo masses are min_halo_mass=1 and max_halo_mass=1e+20.
        """

        a = np.atleast_1d(a)
        k = np.atleast_1d(k)

        int_steps = 2000
        m_msun = np.logspace(
            np.log10(self._params.min_halo_mass),
            np.log10(self._params.max_halo_mass),
            int_steps,
        )

        nu_range = self.mass2nu(m_msun=m_msun, a=a)
        nu_range = np.atleast_2d(nu_range)

        rv_mpc = self.rvir(m_msun, a)
        rv_mpc = np.atleast_2d(rv_mpc)

        c = self.cm(m_msun, a)
        c = np.atleast_2d(c)

        f = self.f(nu=nu_range, a=a)
        bias = self.lin_halo_bias_of_nu(nu_range, a)

        # adapting the multiplicity function and the bias to satisfy the normalization condition
        # corrections to the first mass bin that is used
        # corrections such that int(f dnu)=1 and int(f*b dnu)=1. But just for if we integrate below one solar mass.
        if self._params.min_halo_mass <= 1.0:
            delta_nu = nu_range[:, 1] - nu_range[:, 0]
            diff_f = 1 - np.trapezoid(f, nu_range)
            const_f = diff_f / delta_nu * 2.0
            f[:, 0] += const_f

            diff_bf = 1 - np.trapezoid(f * bias, nu_range)
            const_b = diff_bf / (delta_nu * f[:, 0]) * 2.0
            bias[:, 0] += const_b

        pk_lin = self._lin_pert.powerspec_a_k(k=k, a=a)
        integral_2halo = cython_integral_halo_2h(
            k,
            m_msun,
            nu_range,
            bias,
            rv_mpc,
            c,
            a,
            f,
            self._params.halo_profile,
            adaptive=1,
        )
        rho_m = self.rho_m(a)

        pk_2h = (
            pk_lin
            * integral_2halo**2
            * self._params.rho_matter_Msun_iMpc3**2
            / rho_m**2
        )

        return pk_2h

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        r"""
        Calculates the non-linear matter power spectrum using the Halo Model,
        described e.g. in Mo et al. "Galaxy Formation and Evolution" (2010) chapter 7.6,
        as the sum of the :meth:`pk_1h` and :meth:`pk_2h` terms.

        :param k: Wavelength :math:`[Mpc^{-1}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: Halo Model power spectrum, :math:`P_\text{nl}(k, a)`, in :math:`[Mpc^{3}]`

        Example on how to use the Halo model, set the multiplicity function,
        linear halo bias, halo profile, and the minimal and maximal halo masses in
        solar masses :math:`[M_{\odot}]` considered in the calculation,
        and then calculate the power spectrum:

        .. code-block:: python

            cosmo.set(pk_nonlin_type='HaloModel',
                      multiplicity_fnct=option_mf,
                      lin_halo_bias_type=option_b,
                      halo_profile=option_p,
                      min_halo_mass=1e8,
                      max_halo_mass=1e14)

            pk = cosmo.nonlin_pert.powerspec_a_k(a,k)

        where the possible *option_mf* are given in the documentation to
        :math:`f(\nu, a)`, *option_b* in the documentation to the linear halo bias
        and *option_p* is either True for a NFW-profile or False for assumed point
        sources. Default values for the minimal and maximal halo masses are
        min_halo_mass=1 and max_halo_mass=1e+20.
        """

        a = np.atleast_1d(a).astype(float)
        k = np.atleast_1d(k).astype(float)

        a_limit = np.min(1 / (1 + self.max_redshift(k)))
        mask_invalid = (a <= a_limit) | (a > 1.0)
        a[mask_invalid] = a_limit

        if diag_only:
            assert len(a) == len(k)

        pk_1h = self.pk_1h(k, a)
        pk_2h = self.pk_2h(k, a)
        pk = pk_1h + pk_2h

        pk[:, mask_invalid] = np.nan

        if diag_only:
            return np.diag(pk)
        else:
            return pk

    def print_params(self):
        """
        Prints the cosmological setup and the parameters used for the computation of the
        non-linear matter power spectrum with the halo model.

        Example:

        .. code-block:: python

            cosmo.set(pk_nonlin_type='HaloModel')
            cosmo.nonlin_pert.print_params()
        """

        print("The halomodel has been initialised with the following attributes:")
        for key in self._params.keys():
            print("{}={}".format(key, self._params[key]))
