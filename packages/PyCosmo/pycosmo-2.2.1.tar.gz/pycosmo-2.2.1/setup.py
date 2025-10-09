#!/usr/bin/env python
import numpy
from Cython.Build import cythonize
from setuptools import Extension, setup

files = [
    "const.c",
    "main.c",
    "polevl.c",
    "sici.c",
    "sicif.c",
    "polevlf.c",
    "logf.c",
    "sinf.c",
    "constf.c",
    "mtherr.c",
]
ext_modules = []


for stem in (
    "halo_integral",
    "halo_integral_1h",
    "halo_integral_2h",
    "halo_integral_HI_1h",
    "halo_integral_HI_2h",
    "rho_HI_integral",
    "rho_m_integral",
):
    ext_modules.append(
        Extension(
            name=f"PyCosmo.cython.{stem}",
            ext_modules=cythonize(f"src/PyCosmo/cython/{stem}.pyx"),
            sources=["src/PyCosmo/cython/" + file for file in files + [stem + ".c"]],
            include_dirs=[numpy.get_include()],
        )
    )

setup(
    ext_modules=ext_modules,
)
