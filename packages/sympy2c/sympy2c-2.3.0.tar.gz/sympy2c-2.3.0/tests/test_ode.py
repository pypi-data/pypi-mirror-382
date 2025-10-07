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

from sympy2c import Globals, Module, Ode, Symbol, Vector
from sympy2c.utils import align


def test_ode_solver(tmpdir, compile_and_load):
    v1x, v2x, v1y, v2y = map(Symbol, "v1x v2x v1y v2y".split())
    p1x, p2x, p1y, p2y = map(Symbol, "p1x p2x p1y p2y".split())

    m1, m2 = map(Symbol, "m1 m2".split())

    t = Symbol("t")

    p1x_dot = v1x
    p1y_dot = v1y

    p2x_dot = v2x
    p2y_dot = v2y

    d2 = ((p1x - p2x) ** 2 + (p1y - p2y) ** 2) ** 0.5

    v1x_dot = -m2 * (p1x - p2x) / d2**3
    v1y_dot = -m2 * (p1y - p2y) / d2**3

    v2x_dot = -m1 * (p2x - p1x) / d2**3
    v2y_dot = -m1 * (p2y - p1y) / d2**3

    ode = Ode(
        "planets",
        t,
        [p1x, p1y, p2x, p2y, v1x, v1y, v2x, v2y],
        [p1x_dot, p1y_dot, p2x_dot, p2y_dot, v1x_dot, v1y_dot, v2x_dot, v2y_dot],
        compute_jacobian=True,
    )

    module = Module()
    module.add(Globals(m1, m2))
    module.add(ode)

    _check(module, tmpdir, True, compile_and_load)
    _check(module, tmpdir, False, compile_and_load)

    assert module.get_unique_id() is not None


def _check(module, tmpdir, use_jacobian, compile_and_load):
    wrapper = compile_and_load(module)

    assert wrapper.get_unique_id() is not None

    wrapper.globals.m1 = 2
    wrapper.globals.m2 = 1

    p1 = (5, 0)
    v1 = (0.2, -0.2)

    p2 = (10, 0)
    v2 = (0, 0.5)

    t = np.linspace(0, 60, 1000)

    assert wrapper.solve_planets.__doc__.startswith(
        "solve_planets(y0, tgrid, atol, rtol, max_iter, max_order, use_jacobian)"
    )

    y, meta = wrapper.solve_planets(
        np.array((p1[0], p1[1], p2[0], p2[1], v1[0], v1[1], v2[0], v2[1]), dtype=float),
        t,
        1e-5,
        1e-5,
        use_jacobian=use_jacobian,
    )

    assert isinstance(meta, dict)

    # unpack columns:
    p1x, p1y, p2x, p2y, v1x, v1y, v2x, v2y = y.T

    is_ = [
        p1x.mean(),
        p1y.mean(),
        p2x.mean(),
        p2y.mean(),
        p1x.std(),
        p1y.std(),
        p2x.std(),
        p2y.std(),
    ]

    tobe = [
        10.419238674733615,
        1.4668800402967992,
        11.161522650532781,
        0.06623991940640099,
        2.6002221952237,
        1.3737285646379265,
        2.885845577081757,
        2.0178019356054047,
    ]

    rel_diffs = [abs(i - t) / abs(t) for (i, t) in zip(is_, tobe)]
    assert all([rel_diff < 1e-8 for rel_diff in rel_diffs])

    assert wrapper.symbols_planets() == [
        "p1x",
        "p1y",
        "p2x",
        "p2y",
        "v1x",
        "v1y",
        "v2x",
        "v2y",
    ]


def test_ode_declaration(tmpdir, compile_and_load):
    code = align(
        """
    |decl("p1x", "p2x", "p1y", "p2y",
    |     "v1x", "v2x", "v1y", "v2y",
    |     "t")
    |
    |m1, m2 = map(Symbol, "m1 m2".split())
    |
    |globals = [m1, m2]
    |
    |p1x_dot = v1x
    |p1y_dot = v1y
    |
    |p2x_dot = v2x
    |p2y_dot = v2y
    |
    |d2 = ((p1x - p2x) ** 2 + (p1y - p2y) ** 2) ** .5
    |
    |v1x_dot = -m2 * (p1x - p2x) / d2 ** 3
    |v1y_dot = -m2 * (p1y - p2y) / d2 ** 3
    |
    |v2x_dot = -m1 * (p2x - p1x) / d2 ** 3
    |v2y_dot = -m1 * (p2y - p1y) / d2 ** 3
    |
    |Ode(
    |    "planets",
    |    t,
    |    [p1x, p1y, p2x, p2y, v1x, v1y, v2x, v2y],
    |    [p1x_dot, p1y_dot, p2x_dot, p2y_dot, v1x_dot, v1y_dot, v2x_dot, v2y_dot],
    |    compute_jacobian=False
    |)
    |
    |"""
    )

    module, _ = Module.parse_sympy_code(code)
    assert module.get_unique_id() is not None
    _check(module, tmpdir, False, compile_and_load)
    with pytest.raises(AssertionError) as e:
        _check(module, tmpdir, True, compile_and_load)

    assert "compute_jacobian" in str(e.value), str(e.value)


def test_rorbertsons_reaction_example(tmpdir, compile_and_load):
    # school book example for numerical issues with a stiff ODE.

    y = Vector("yi", 3)
    t = Symbol("t")

    ydot = [None, None, None]
    ydot[0] = 1.0e4 * y[1] * y[2] - 0.04e0 * y[0]
    ydot[2] = 3.0e7 * y[1] * y[1]
    ydot[1] = -1.0 * (ydot[0] + ydot[2])

    ode = Ode("robertson", t, y, ydot, compute_jacobian=False)
    module = Module()
    module.add(ode)
    assert module.get_unique_id() is not None
    wrapper = compile_and_load(module)
    assert wrapper.get_unique_id() is not None

    y0 = np.array((1.0, 0.0, 0.0))

    tvec = 0.4 * 10 ** np.arange(1.0, 13.0)

    y_numerical, _ = wrapper.solve_robertson(y0, tvec, 1e-5, 1e-5, use_jacobian=False)

    tobe = np.array(
        [
            [1.00000000e00, 0.00000000e00, 0.00000000e00],
            [7.26396624e-01, 9.60786191e-06, 2.73593768e-01],
            [4.51749939e-01, 3.23854684e-06, 5.48246822e-01],
            [1.83279161e-01, 8.94691224e-07, 8.16719945e-01],
            [3.89748728e-02, 1.62139825e-07, 9.61024965e-01],
            [4.93229552e-03, 1.98257581e-08, 9.95067685e-01],
            [5.13206276e-04, 2.05385553e-09, 9.99486792e-01],
            [5.25780257e-05, 2.10322585e-10, 9.99947422e-01],
            [4.79111031e-06, 1.91645284e-11, 9.99995209e-01],
            [-1.99506786e-07, -7.98020732e-13, 1.00000020e00],
            [1.12615228e-06, 4.50460967e-12, 9.99998874e-01],
            [-5.71582448e-06, -2.28633004e-11, 1.00000572e00],
        ]
    )

    assert np.allclose(y_numerical, tobe)

    ode = Ode("robertson", t, y, ydot, compute_jacobian=True)
    module = Module()
    module.add(ode)
    assert module.get_unique_id() is not None

    wrapper = compile_and_load(module)
    assert wrapper.get_unique_id() is not None

    rtol = 1e-4
    atol = np.array([1e-6, 1e-10, 1e-6])

    y, _ = wrapper.solve_robertson(y0, tvec, rtol, atol, use_jacobian=True)

    tobe = np.array(
        [
            [1.00000000e00, 0.00000000e00, 0.00000000e00],
            [7.26427754e-01, 9.60916477e-06, 2.73562637e-01],
            [4.51778459e-01, 3.23889933e-06, 5.48218302e-01],
            [1.83293589e-01, 8.94748423e-07, 8.16705516e-01],
            [3.89904526e-02, 1.62207632e-07, 9.61009385e-01],
            [4.93640957e-03, 1.98424000e-08, 9.95063571e-01],
            [5.16183750e-04, 2.06578837e-09, 9.99483814e-01],
            [5.17980795e-05, 2.07202864e-10, 9.99948202e-01],
            [5.28360449e-06, 2.11345258e-11, 9.99994716e-01],
            [4.65880673e-07, 1.86352351e-12, 9.99999534e-01],
            [1.42835178e-08, 5.71341234e-14, 9.99999986e-01],
            [1.28379931e-07, 5.13519724e-13, 9.99999872e-01],
        ]
    )

    assert np.allclose(y, tobe)
