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


import numpy as np

from PyCosmo.cython.halo_integral_HI_1h import _integral_halo as cython_integral_HI_1h
from PyCosmo.cython.halo_integral_HI_2h import _integral_halo as cython_integral_HI_2h
from PyCosmo.cython.rho_HI_integral import _integral_halo as cython_integral_rho_HI
from PyCosmo.NonLinearPerturbation_HaloModel import NonLinearPerturbation_HaloModel

"""
Written by:

    Pascal Hitz
    Institute for Particle Physics and Astrophysics
    ETH Zurich
    hitzpa@phys.ethz.ch

"""


class NonLinearPerturbation_HI(NonLinearPerturbation_HaloModel):
    r"""
    The class incorporates the implementation of the Halo Model for neutral hydrogen
    (HI) as described in `Padmanabhan et al., 2017 <https://arxiv.org/abs/1611.06235>`_.

    This can be set as:

        .. code-block:: python

            cosmo.set(pk_nonlin_type='HI')

    .. Warning ::
        NonLinearPerturbation_HI not supported by the Boltzmann solver yet.
        Calling any function from this module while using the Boltzmann solver (pk_type
        = 'boltz') will return
        **AttributeError: 'NoneType' object has no attribute 'function'**
    """

    # Inherit properties and methods of NonLinearPerturbation_HaloModel
    def __init__(self, cosmo):
        super().__init__(cosmo)

        # Parameters for MHI-M model:
        # Padmanabhan et al., 'A halo model for cosmological neutral hydrogen: abundances and clustering', (2017)
        self._params.a_hi = 0.09
        self._params.b_hi = -0.58
        self._params.v0_hi = 10**1.56
        self._params.f_hi = (
            (1 - self._params.Yp) * self._params.omega_b / self._params.omega_m
        )

        self._params.c_hi0 = 28.65
        self._params.gamma = 1.45

    def mhi_of_m(self, m_msun, a, diag_only=False):
        r"""
        HI-halo mass relation: Calculates the amount of HI mass in a dark matter halo of
        mass :math:`M`.

        :param m_msun: Halo mass in solar masses :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor a, scalar or 1d array
        :return: HI mass in solar masses :math:`[M_{\odot}]`
        """
        a = np.atleast_1d(a)
        vc = self.vvir(m_msun, a, diag_only=diag_only)
        mhi = (
            self._params.a_hi
            * self._params.f_hi
            * m_msun
            * (m_msun * self._params.h / (1e11)) ** self._params.b_hi
            * np.exp(-((self._params.v0_hi / vc) ** 3))
        )
        mhi[np.isnan(mhi)] = 0.0

        return mhi

    def c_hi(self, m_msun, a):
        r"""
        *Concentration-mass* function of HI halos.

        :param m_msun: Halo mass in solar masses :math:`[M_{\odot}]`, scalar or 1d array
        :param a: Scale factor a, scalar or 1d array
        :return: Concentration :math:`c_\text{HI}(M, a)` of a halo mass :math:`[M_{\odot}]` at scale factor :math:`a`
        """
        a = np.atleast_1d(a)
        chi = (
            self._params.c_hi0
            * (m_msun / 1e11) ** (-0.109)
            * 4
            * a[:, None] ** self._params.gamma
        )
        return chi

    def rho_HI(self, a):
        r"""
        Calculates the mean HI density as a function of the scale factor.

        :param a: Scale factor, scalar or 1d array
        :return: Mean HI density, in :math:`[M_{\odot} \ Mpc^{-3}]`

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

        mhi_msun = self.mhi_of_m(m_msun, a)

        f = self.f(nu=nu_range, a=a)

        # adapting the multiplicity function to satisfy the normalization condition
        # corrections to the first mass bin that is used
        # corrections such that int(f dnu)=1. But just if we integrate below one solar mass.
        if self._params.min_halo_mass <= 1.0:
            delta_nu = nu_range[:, 1] - nu_range[:, 0]
            diff_f = 1 - np.trapezoid(f, nu_range)
            const_f = diff_f / delta_nu * 2.0
            f[:, 0] += const_f

        integral_rho_HI = cython_integral_rho_HI(
            k, m_msun, mhi_msun, nu_range, a, f, adaptive=1
        )
        rho_HI_total = integral_rho_HI * self._params.rho_matter_Msun_iMpc3

        return rho_HI_total

    def pk_HI_1h(self, k, a):
        r"""
        One-halo term :math:`P_\text{HI,1h}(k, a)` of the non-linear HI power spectrum as
        described in the Halo Model for HI.

        :param k: Wavelength :math:`[Mpc^{-1}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: One-Halo power spectrum :math:`P_\text{HI,1h}(k, a) \ [Mpc^{3}]`

        Example of setting the multiplicity function, linear halo bias, halo profile,
        and the assumed minimal and maximal halo masses in solar masses :math:`[M_{\odot}]`
        considered in the calculation:

        .. code-block:: python

            cosmo.set(multiplicity_fnct=option_mf,
                      lin_halo_bias_type=option_b,
                      halo_profile=option_p,
                      min_halo_mass=1e8,
                      max_halo_mass=1e14)

        where the possible *option_mf* are given in the documentation to
        :math:`f(\nu, a)` and *option_b* in the documentation to the linear halo bias
        in the NonLinearPerturbation_HaloModel module.
        *option_p* is either True for a NFW-profile or False for assumed point
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

        mhi_msun = self.mhi_of_m(m_msun, a)

        rv_mpc = self.rvir(m_msun, a)
        rv_mpc = np.atleast_2d(rv_mpc)

        c = self.c_hi(m_msun, a)
        c = np.atleast_2d(c)

        f = self.f(nu=nu_range, a=a)

        # adapting the multiplicity function to satisfy the normalization condition
        # corrections to the first mass bin that is used
        # corrections such that int(f dnu)=1. But just for if we integrate below one solar mass.
        if self._params.min_halo_mass <= 1.0:
            delta_nu = nu_range[:, 1] - nu_range[:, 0]
            diff_f = 1 - np.trapezoid(f, nu_range)
            const_f = diff_f / delta_nu * 2.0
            f[:, 0] += const_f

        integral_HI_1h = cython_integral_HI_1h(
            k,
            m_msun,
            mhi_msun,
            nu_range,
            rv_mpc,
            c,
            a,
            f,
            self._params.halo_profile,
            adaptive=1,
        )

        rho_HI = self.rho_HI(a)

        pk_1h = integral_HI_1h * self._params.rho_matter_Msun_iMpc3 / rho_HI**2

        return pk_1h

    def pk_HI_2h(self, k, a):
        r"""
        Two-halo term :math:`P_\text{HI,2h}(k, a)` of the non-linear power spectrum as
        described in the Halo Model for HI.

        :param k: Wavelength :math:`[Mpc^{-1}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: Two-Halo power spectrum :math:`P_\text{HI,2h}(k, a) \ [Mpc^{3}]`

        Example of setting the multiplicity function, linear halo bias, halo profile,
        and the assumed minimal and maximal halo masses in solar masses :math:`[M_{\odot}]`
        considered in the calculation:

        .. code-block:: python

            cosmo.set(multiplicity_fnct=option_mf,
                      lin_halo_bias_type=option_b,
                      halo_profile=option_p,
                      min_halo_mass=1e8,
                      max_halo_mass=1e14)

        where the possible *option_mf* are given in the documentation to
        :math:`f(\nu, a)` and *option_b* in the documentation to the linear halo bias
        in the NonLinearPerturbation_HaloModel module.
        *option_p* is either True for a NFW-profile or False for assumed point
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

        mhi_msun = self.mhi_of_m(m_msun, a)

        rv_mpc = self.rvir(m_msun, a)
        rv_mpc = np.atleast_2d(rv_mpc)

        c = self.c_hi(m_msun, a)
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

        integral_HI_2h = cython_integral_HI_2h(
            k,
            m_msun,
            mhi_msun,
            nu_range,
            bias,
            rv_mpc,
            c,
            a,
            f,
            self._params.halo_profile,
            adaptive=1,
        )
        rho_HI = self.rho_HI(a)

        pk_2h = (
            pk_lin
            * integral_HI_2h**2
            * self._params.rho_matter_Msun_iMpc3**2
            / rho_HI**2
        )

        return pk_2h

    def powerspec_a_k_HI(self, a=1.0, k=0.1, diag_only=False):
        r"""
        Calculates the non-linear HI power spectrum using the Halo Model for HI,
        as the sum of the :meth:`pk_HI_1h` and :meth:`pk_HI_2h` terms.


        :param k: Wavelength :math:`[Mpc^{-1}]`, scalar or 1d array
        :param a: Scale factor, scalar or 1d array
        :return: HI Halo Model power spectrum, :math:`P_\text{HI,nl}(k, a)`, in :math:`[Mpc^{3}]`

        Example on how to use the HI Halo model, set the multiplicity function,
        linear halo bias, halo profile, and the minimal and maximal halo masses in
        solar masses :math:`[M_{\odot}]` considered in the calculation,
        and then calculate the power spectrum:

        .. code-block:: python

            cosmo.set(pk_nonlin_type='HI',
                      multiplicity_fnct=option_mf,
                      lin_halo_bias_type=option_b,
                      halo_profile=option_p,
                      min_halo_mass=1e8,
                      max_halo_mass=1e14)

            pk = cosmo.nonlin_pert.powerspec_a_k_HI(a,k)

        where the possible *option_mf* are given in the documentation to
        :math:`f(\nu, a)` and *option_b* in the documentation to the linear halo bias
        in the NonLinearPerturbation_HaloModel module.
        *option_p* is either True for a NFW-profile or False for assumed point
        sources.
        Default values for the minimal and maximal halo masses are
        min_halo_mass=1 and max_halo_mass=1e+20.
        """
        a = np.atleast_1d(a).astype(float)
        k = np.atleast_1d(k).astype(float)

        a_limit = np.min(1 / (1 + self.max_redshift(k)))
        mask_invalid = (a <= a_limit) | (a > 1.0)
        a[mask_invalid] = a_limit

        if diag_only:
            assert len(a) == len(k)

        pk_HI_1h = self.pk_HI_1h(k, a)
        pk_HI_2h = self.pk_HI_2h(k, a)
        pk_HI = pk_HI_1h + pk_HI_2h

        pk_HI[:, mask_invalid] = np.nan

        if diag_only:
            return np.diag(pk_HI)
        else:
            return pk_HI

    def mean_hi_temp(self, a):
        r"""
        Calculates the mean HI brightness temperature :math:`T_\text{b}(a)` in :math:`[K]` as a function of the scale factor.

        :param a: Scale factor, scalar or 1d array
        :return: Mean HI brightness temperature, in :math:`[K]`
        """
        a = np.atleast_1d(a).astype(float)
        rho_HI = self.rho_HI(a=a)

        Tb = (
            3
            * self._params.hbar
            * self._params.c**3
            * self._params.A10
            / (16 * self._params.kb * self._params.f12**2 * self._params.mp)
            * rho_HI
            / (self._background.H(a) * a**2)
        )

        unit_K = self._params.msun / self._params.evc2 / self._params.mpc**2

        Tb *= unit_K

        return Tb

    def powerspec_a_k(self, a=1.0, k=0.1, diag_only=False):
        return super().powerspec_a_k(a, k, diag_only)
