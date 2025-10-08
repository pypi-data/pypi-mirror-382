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


import pickle
import warnings

import numpy as np
import pytest
import sympy as sp

from sympy2c import (
    ERROR,
    Alias,
    Checked,
    Function,
    Globals,
    IfThenElse,
    Integral,
    InterpolationFunction1D,
    Module,
    Symbol,
    Vector,
    isnan,
    symbols,
)


@pytest.fixture
def x():
    return Symbol("x")


@pytest.fixture
def y():
    return Symbol("y")


def test_finite_integral_qng_and_qag(tmpdir, compile_and_load):
    a, b, x = map(Symbol, "abx")
    integrand = 1 + (a + x) * x

    integral = Integral(integrand, x, 0, b)

    m = Module()
    m.add(Globals(b))
    m.add(Function("integral", integral, a))

    assert m.get_unique_id() is not None

    module = compile_and_load(m)
    assert module.get_unique_id() is not None
    # w = m.get_module_wrapper().setup_wrappers()
    # module = compile_and_load(m)
    module.set_quadpack_method("default", "QNG")
    module.set_eps_rel("default", 1e-5)
    module.set_eps_abs("default", 0)
    module.set_max_intervals("default", 1000)

    module.globals.b = 1
    assert abs(module.integral(0) - 1 - 1 / 3) < 1e-8
    assert module.get_abs_err("default") < 1e-13
    assert module.get_rel_err("default") < 1e-13

    assert abs(module.integral(1) - 1.5 - 1 / 3) < 1e-8
    assert module.get_abs_err("default") < 1e-13
    assert module.get_rel_err("default") < 1e-13

    module.set_quadpack_method("default", "QAG")
    module.globals.b = 1
    assert abs(module.integral(0) - 1 - 1 / 3) < 1e-8
    assert module.get_abs_err("default") < 1e-13
    assert module.get_rel_err("default") < 1e-13

    assert abs(module.integral(1) - 1.5 - 1 / 3) < 1e-8
    assert module.get_abs_err("default") < 1e-13
    assert module.get_rel_err("default") < 1e-13

    module.globals.b = None
    assert np.isnan(module.globals.b)


def test_infinite_integrals(tmpdir, compile_and_load):
    center = Symbol("center")
    x = Symbol("x")
    integrand = sp.exp(-sp.exp((x - center) ** 2))

    integral_1 = Integral(integrand, x, -sp.oo, sp.oo)
    integral_2 = Integral(integrand, x, center, sp.oo)
    integral_3 = Integral(integrand, x, -sp.oo, center)

    m = Module()
    m.add(Function("integral_1", integral_1, center))
    m.add(Function("integral_2", integral_2, center))
    m.add(Function("integral_3", integral_3, center))

    module = compile_and_load(m)
    module.set_quadpack_method("default", "QAGI")
    module.set_eps_rel("default", 1e-5)
    module.set_eps_abs("default", 0)
    module.set_max_intervals("default", 1000)

    expected_value = 0.5266003665440283

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        assert abs(module.integral_1(0) - expected_value) < 1e-10
        assert abs(module.integral_1(1) - expected_value) < 1e-10

        assert abs(module.integral_2(0) - expected_value / 2) < 1e-10
        assert abs(module.integral_2(1) - expected_value / 2) < 1e-10

        assert abs(module.integral_3(0) - expected_value / 2) < 1e-10
        assert abs(module.integral_3(1) - expected_value / 2) < 1e-10


def test_vector_symbol(tmpdir, compile_and_load):
    a = Vector("a", 3)
    x = Symbol("x")
    y = Symbol("y")

    expression = a[0] * Integral(a[1] * x + y, x, 0, a[2])

    m = Module()
    m.add(Function("fun", expression, a, y))
    assert m.get_unique_id() is not None

    module = compile_and_load(m)

    module.set_quadpack_method("default", "QAG")
    module.set_eps_rel("default", 1e-5)
    module.set_eps_abs("default", 0)
    module.set_max_intervals("default", 1000)

    assert module.fun(np.array([0.0, 0.0, 0.0]), 0.0) == 0
    assert module.fun(np.array([1.0, 1.0, 0.0]), 0.0) == 0
    assert abs(module.fun(np.array([1.0, 1.0, 1.0]), 0.0) - 0.5) < 1e-8
    assert abs(module.fun(np.array([2.0, 1.0, 1.0]), 0.0) - 1.0) < 1e-8


def test_vector_valued_functions(tmpdir, compile_and_load):
    a = Vector("a", 3)

    expressions = [a[0] * a[1], a[1] * a[2], a[0] * a[2]]
    f = Function("a", expressions, a)

    m = Module()
    m.add(f)
    module = compile_and_load(m)

    assert np.all(module.a(np.arange(1, 4, dtype=float)) == np.array([2.0, 6.0, 3.0]))

    from numba import njit

    aa = module.a

    @njit
    def compute():
        return aa(np.arange(1.0, 4.0))

    compute()


def test_alias(tmpdir, compile_and_load):
    x = Symbol("x")
    y = Symbol("y")
    z = Symbol("z")

    expressions = [x * y, y * z, x * z]

    a = Alias("a", x, y, z)

    f = Function("a", expressions, a)

    m = Module()
    m.add(f)
    module = compile_and_load(m)

    assert np.all(module.a(np.arange(1, 4, dtype=float)) == np.array([2.0, 6.0, 3.0]))


def test_interpolation(tmpdir, compile_and_load):
    x = Symbol("x")

    f = InterpolationFunction1D("f")

    m = Module()
    m.add(Function("f_interp", f(x) + x, x))
    assert m.get_unique_id() is not None

    module = compile_and_load(m)

    with pytest.raises(ArithmeticError):
        module.f_interp(1)
    assert module.get_last_error_message() == "you must call set_f_values first"

    x = np.linspace(0, 1, 100)
    y = x**2

    module.set_f_values(x, y + 1)
    assert module.f_interp(0.0) == 1

    assert module.f_interp(1.0) == 3

    assert np.all(module.ip_sorted_f(x) + x == module.f_interp(x))

    # check boundaries:
    assert np.allclose(module.ip_sorted_f(np.array([0.99])), [1.0 + 0.99**2], atol=1e-5)
    assert np.allclose(module.ip_sorted_f(np.array([1.0])), [1.0 + 1.0], atol=1e-5)
    assert np.allclose(module.ip_sorted_f(np.array([1e-6])), [1.0 + 1e-12], atol=1e-5)
    assert np.allclose(module.ip_sorted_f(np.array([0.0])), [1.0 + 0.0], atol=1e-5)

    assert np.all(np.isnan(module.ip_sorted_f(np.array([1.00000001]))))
    assert np.all(np.isnan(module.ip_sorted_f(np.array([-1e-10]))))

    # set aggain
    module.set_f_values(x, y)

    assert module.f_interp(0.0) == 0
    assert module.f_interp(1.0) == 2

    h = x[1] - x[0]
    assert abs(module.f_interp(0.5) - 0.75) <= h**2 / 4

    # continuation to the right is ok:
    module.f_interp(1.1)
    with pytest.raises(ArithmeticError):
        module.f_interp(-0.1)

    assert module.get_last_error_message() == "spline eval failed: input domain error"

    assert np.all(x == module.get_x_f())
    assert np.all(y == module.get_y_f())

    m_back = pickle.loads(pickle.dumps(module))
    assert np.all(x == m_back.get_x_f())
    assert np.all(y == m_back.get_y_f())

    assert m_back.f_interp(1.1) == module.f_interp(1.1)


def test_error_and_checked(tmpdir, compile_and_load):
    a = Symbol("a")
    expression = IfThenElse(a <= 0, ERROR("can not take log"), sp.log(a))

    f = Function("f", expression, a)

    a_checked = Checked(a >= 0, "a must not be negative")
    g = Function("g", sp.sqrt(a_checked), a)

    h = Function("h", IfThenElse(isnan(a), 1.0, 2.0), a)

    m = Module()
    m.add(f)
    m.add(g)
    m.add(h)
    module = compile_and_load(m)

    assert module.f(1.0) == 0.0
    assert module.g(0.0) == 0.0
    assert module.g(1.0) == 1.0
    assert module.g(4.0) == 2.0

    assert module.h(np.nan) == 1.0
    assert module.h(1.0) == 2.0

    with pytest.raises(ArithmeticError):
        module.f(0)

    assert "can not take log" in module.get_last_error_message()

    with pytest.raises(ArithmeticError):
        module.g(-1)

    assert "a must not be negative" in module.get_last_error_message()


def test_integrals(compile_and_load):
    a, b, c, d, e = symbols("a b c d e")

    m = Module()
    ii = Integral(a + b * c, c, 1, a)
    f = Function("f", ii, a, b)
    m.add(f)

    jj = Integral(a + b * c, c, d, e)
    g = Function("g", jj, a, b, d, e)
    m.add(g)
    compile_and_load(m)
