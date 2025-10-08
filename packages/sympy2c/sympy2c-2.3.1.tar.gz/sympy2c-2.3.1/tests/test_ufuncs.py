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

from sympy2c import Function, Module, Symbol


def test_unfunc(compile_and_load):
    a = Symbol("a")
    b = Symbol("b")

    f = Function("add", a + b, a, b)
    m = Module()
    m.add(f)
    w = compile_and_load(m)

    assert w.add(1, 2) == 3

    a_vec = np.arange(3.0)
    b_vec = np.arange(3.0)

    assert np.all(w.add(a_vec, b_vec) == a_vec + b_vec)

    a_vec = np.array((7.0,))
    b_vec = np.arange(3.0)

    assert np.all(w.add(a_vec, b_vec) == a_vec + b_vec)
    assert np.all(w.add_ufunc(a_vec, b_vec) == a_vec + b_vec)

    a_vec = np.arange(4.0)
    b_vec = np.arange(3.0)[:, None]

    assert np.all(w.add(a_vec, b_vec) == a_vec + b_vec)
