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

import re

import numpy as np
import pytest

from sympy2c import (
    Function,
    Globals,
    Integral,
    InterpolationFunction1D,
    Module,
    Symbol,
    Vector,
    __version__,
)
from sympy2c.utils import align


def test_minimal(tmpdir, compile_and_load):
    x, y, z, alpha, da = map(Symbol, "x y z alpha da".split())

    v = Vector("v", 3)

    m = Module()

    m.add(Globals(y, z, alpha, v))

    _squared = InterpolationFunction1D("squared")

    m.add(Function("f", x * y + z ** _squared(alpha), x))
    m.add(Function("integral", Integral(_squared(da), da, 0, x), x))
    m.add(Function("squared", _squared(x), x))
    m.add(Function("sumv", v[0] + v[1] + v[2]))

    version = "_".join(map(str, __version__))
    assert m.get_unique_id().startswith(f"{version}_"), m.get_unique_id()

    m_loaded = compile_and_load(m)

    assert m_loaded.sympy2c_version is not None
    assert re.match(r"\d+\.\d+\.\d+", m_loaded.sympy2c_version)

    x = np.linspace(0, 1, 100)
    m_loaded.set_squared_values(x, x**2)
    assert m_loaded.squared(1) == 1
    assert abs(m_loaded.squared(0.5) - 0.5**2) < 1e-10

    m_loaded.globals.y = 1
    m_loaded.globals.z = 2
    m_loaded.globals.alpha = 0.5
    m_loaded.globals.v = np.arange(3)

    assert m_loaded.sumv() == 3.0

    assert m_loaded.globals.y == 1
    with pytest.raises(KeyError):
        m_loaded.globals.u

    print(m_loaded.globals)

    assert abs(m_loaded.f(2) - 3.189207115002721) < 1e-14
    assert abs(m_loaded.integral(1) - 1 / 3) < 1e-7

    assert m_loaded.get_unique_id() is not None


def test_from_code_snippet(tmpdir, compile_and_load):
    code = align(
        """
            |decl("a", "b", "c", "x")
            |
            |globals = [b]
            |
            |squared = InterpolationFunction1D("squared")
            |
            |f = Function("f", squared(a * b), a)
            |
            |g = Integral(f(c) * c, c, 0, b)
            |g = Function("g", g)
            |
            |h = Function("h", Integral(IfThenElse(x < 1, 1, -0), x, 0, 2))
            |i = Function("i", Min(a, c) + Max(a, c), a, c)
            """
    )

    m, _ = Module.parse_sympy_code(code)
    m_loaded = compile_and_load(m)

    x = np.linspace(0, 1, 100)
    m_loaded.set_squared_values(x, x**2)

    m_loaded.globals.b = 0.5

    assert abs(m_loaded.f(2) - 1) < 1e-8
    assert abs(m_loaded.g() - 0.5**6 / 4) < 1e-8

    assert abs(m_loaded.h() - 1) < 1e-8

    assert m_loaded.get_unique_id() is not None
