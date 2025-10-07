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

from sympy import Abs, sqrt

from sympy2c import Function, Module, Symbol
from sympy2c.expressions import Max, Min


def test_min(tmpdir, compile_and_load):
    a = Symbol("a")
    b = Symbol("b")

    min_f = Function("f", Min(a + b, a * b), a, b)
    max_f = Function("g", Max(a + b, a * b), a, b)

    m = Module()
    m.add(min_f)
    m.add(max_f)

    w = compile_and_load(m)

    assert w.f(1.0, 2.0) == 2.0
    assert w.f(2.0, 1.0) == 2.0

    assert w.g(1.0, 2.0) == 3.0
    assert w.g(2.0, 1.0) == 3.0


def test_abs(tmpdir, compile_and_load):
    a = Symbol("a")

    f1 = Function("f1", sqrt(a**2), a)
    f2 = Function("f2", Abs(a), a)

    m = Module()
    m.add(f1)
    m.add(f2)

    w = compile_and_load(m)

    assert w.f1(1) == 1.0
    assert w.f1(-1) == 1.0

    assert w.f2(1) == 1.0
    assert w.f2(-1) == 1.0


def test_if_symbols_are_real():
    # sympy2c symbols represent real numbers which supports
    # simplifications:
    a = Symbol("a")
    assert sqrt(a * a) == Abs(a)

    # default Symbols are not real, so simplification does not work:
    import sympy

    a = sympy.Symbol("a")
    assert sqrt(a * a) != Abs(a)
