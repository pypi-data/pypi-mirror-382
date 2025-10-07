# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2022 ETH Zurich, Institute for Particle and Astrophysics and SIS
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
import pytest
import scipy.special
import sympy

from sympy2c import Function, Module, symbols
from sympy2c.expressions import hyper_2f1


@pytest.mark.parametrize("name", "ijky")
def test_bessel(name, tmpdir, compile_and_load):
    x, n = symbols("x n")

    sympy_fun = getattr(sympy, "bessel" + name)
    scipy_fun = getattr(scipy.special, name + "v")

    fun = Function("fun", sympy_fun(n * n, x * x), n, x)
    m = Module()
    m.add(fun)
    w = compile_and_load(m)

    assert np.allclose(w.fun(0, 1), scipy_fun(0, 1))
    assert np.allclose(w.fun(0, 2), scipy_fun(0, 4))
    assert np.allclose(w.fun(1, 2), scipy_fun(1, 4))


def test_hyper(tmpdir, compile_and_load):
    a, b, c, x = symbols("a b c x")

    h = Function("h", hyper_2f1(a, b, c, x), a, b, c, x)

    m = Module()
    m.add(h)

    w = compile_and_load(m)

    for args in [(0.1, 1, 1, 0), (2, 1, 4, 1)]:
        assert np.allclose(w.h(*args), scipy.special.hyp2f1(*args))


def test_gamma(tmpdir, compile_and_load):
    (x,) = symbols("x")

    h = Function("h", sympy.gamma(x), x)

    m = Module()
    m.add(h)

    w = compile_and_load(m)

    for x in (1, 2, 3, 3.5):
        assert np.allclose(w.h(x), scipy.special.gamma(x))
