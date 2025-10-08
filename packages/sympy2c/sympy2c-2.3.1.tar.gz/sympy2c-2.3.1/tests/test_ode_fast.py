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

import numpy as np
import sympy as sp

from sympy2c import (
    Function,
    Globals,
    Integral,
    InterpolationFunction1D,
    Module,
    Symbol,
    Vector,
    symbols,
)
from sympy2c.ode import Ode
from sympy2c.ode_fast import OdeFast


def test_lsoda_solver(tmpdir, compile_and_load):
    v1x, v2x, v1y, v2y = symbols("v1x v2x v1y v2y")
    p1x, p2x, p1y, p2y = symbols("p1x p2x p1y p2y")

    t, m1, m2 = symbols("t m1 m2")

    p1x_dot = v1x
    p1y_dot = v1y

    p2x_dot = v2x
    p2y_dot = v2y

    d2 = ((p1x - p2x) ** 2 + (p1y - p2y) ** 2) ** 0.5

    v1x_dot = -m2 * (p1x - p2x) / d2**3
    v1y_dot = -m2 * (p1y - p2y) / d2**3

    v2x_dot = -m1 * (p2x - p1x) / d2**3
    v2y_dot = -m1 * (p2y - p1y) / d2**3

    ode_0 = OdeFast(
        "planets_0",
        t,
        [p1x, p1y, p2x, p2y, v1x, v1y, v2x, v2y],
        [p1x_dot, p1y_dot, p2x_dot, p2y_dot, v1x_dot, v1y_dot, v2x_dot, v2y_dot],
    )

    # we crate same solver again to check if overlap creates compilation issues:
    ode_1 = OdeFast(
        "planets_1",
        t,
        [p1x, p1y, p2x, p2y, v1x, v1y, v2x, v2y],
        [p1x_dot, p1y_dot, p2x_dot, p2y_dot, v1x_dot, v1y_dot, v2x_dot, v2y_dot],
    )

    ode_2 = OdeFast(
        "planets_2",
        t,
        [p1x, p1y, p2x, p2y, v1x, v1y, v2x, v2y],
        [p1x_dot, p1y_dot, p2x_dot, p2y_dot, v1x_dot, v1y_dot, v2x_dot, v2y_dot],
        splits=[4, 6],
    )

    # gamma variable conflicts with C gamma function, thus we use gamma_ instead:
    x, y, alpha, beta, gamma, delta = symbols("x y alpha beta gamma_ delta")

    ode_3 = OdeFast(
        "predator_prey",
        t,
        [x, y],
        [alpha * x - beta * x * y, delta * x * y - gamma * y],
    )

    module = Module()
    module.add(Globals(m1, m2, alpha, beta, gamma, delta))
    module.add(ode_0)
    module.add(ode_1)
    module.add(ode_2)
    module.add(ode_3)

    assert module.get_unique_id() is not None

    w = compile_and_load(module)
    assert w.get_unique_id() is not None

    w.globals.m1 = 2
    w.globals.m2 = 1

    w = pickle.loads(pickle.dumps(w))

    p1 = (5, 0)
    v1 = (0.2, -0.2)

    p2 = (10, 0)
    v2 = (0, 0.5)

    t = np.linspace(0, 60, 1000)

    tobe = [
        10.419238664939208,
        1.4668800372218,
        11.161522670121593,
        0.06623992555639961,
        2.6002221831463435,
        1.3737285597860913,
        2.8858456145722458,
        2.017801931489659,
    ]

    for solver in (
        w.solve_fast_planets_0,
        w.solve_fast_planets_1,
        w.solve_fast_planets_2,
    ):
        y = solver(
            np.array(
                (p1[0], p1[1], p2[0], p2[1], v1[0], v1[1], v2[0], v2[1]), dtype=float
            ),
            t,
            1e-5,
            1e-5 * np.ones((8,)),
        )

        result, meta = y

        assert sum(meta["steps"]) == 100
        assert abs(sum(meta["step_sizes"]) - t[-1] + t[0]) < 1e-8

        assert meta["istate"] == 2
        assert meta["new_traces"] == {}

        p1x, p1y, p2x, p2y, v1x, v1y, v2x, v2y = result.T

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

        rel_diffs = [abs(i - t) / abs(t) for (i, t) in zip(is_, tobe)]
        assert all([rel_diff < 1e-8 for rel_diff in rel_diffs])

    w.globals.alpha = 2 / 3
    w.globals.beta = 4 / 3
    w.globals.gamma_ = 1
    w.globals.delta = 1

    t = np.linspace(0, 10, 10)

    result, meta = w.solve_fast_predator_prey(
        np.array((1.0, 0.2)), t, 1e-5, 1e-5 * np.ones((2,))
    )

    tobe = np.array(
        [
            [1.0, 0.2],
            [1.5147443, 0.2638374],
            [1.77945534, 0.57985881],
            [1.09852698, 1.00260696],
            [0.57480453, 0.79116964],
            [0.48529783, 0.45766939],
            [0.6036409, 0.27152023],
            [0.90179806, 0.20262532],
            [1.38857545, 0.23467216],
            [1.79452756, 0.47218948],
        ]
    )

    assert np.allclose(result, tobe)

    assert np.allclose(
        w.planets_0_dot(0.0, np.arange(8.0)),
        np.array([4.0, 5.0, 6.0, 7.0, 0.08838835, 0.08838835, -0.1767767, -0.1767767]),
    )
    assert sum(meta["steps"]) > 0


def test_split(compile_and_load):
    t, y0, y1, y2, y3, y4, y5, y6, alpha = symbols("t y0 y1 y2 y3 y4 y5 y6 alpha")

    ydot0 = -0.04 * y0 + 1e4 * y1 * y2
    ydot2 = 3e7 * y1 * y1
    ydot1 = -ydot0 - ydot2

    ydot3 = y4
    ydot4 = y5
    ydot5 = -(alpha**3) * y3

    ode_baseline = Ode(
        "robertson_baseline",
        t,
        [y0, y1, y2, y3, y4, y5],
        [ydot0, ydot1, ydot2, ydot3, ydot4, ydot5],
    )

    ode_0 = OdeFast(
        "robertson_0",
        t,
        [y0, y1, y2, y3, y4, y5],
        [ydot0, ydot1, ydot2, ydot3, ydot4, ydot5],
        splits=[1],  # can trigger issue with rec_inv related compuations
    )
    ode_1 = OdeFast(
        "robertson_1",
        t,
        [y0, y1, y2, y3, y4, y5],
        [ydot0, ydot1, ydot2, ydot3, ydot4, ydot5],
        splits=[2, 5],  # trigger multiple splits
    )
    ode_2 = OdeFast(
        "robertson_2",
        t,
        [y0, y1, y2, y3, y4, y5],
        [ydot0, ydot1, ydot2, ydot3, ydot4, ydot5],
    )

    module = Module()
    module.add(ode_baseline)
    module.add(ode_0)
    module.add(ode_1)
    module.add(ode_2)
    module.add(Globals(alpha))

    wrapper = compile_and_load(module)

    tvec = 0.4 * 10 ** np.arange(0, 6)
    rtol = 1e-6
    atol = np.array([1e-9, 1e-8, 1e-10, 1e-8])
    atol = 1e-8

    alpha = 1e-4
    wrapper.globals.alpha = alpha
    y0 = np.array([1.0, 0.0, 0.0, 1.0, -alpha, alpha**2])

    result_baseline, meta_baseline = wrapper.solve_robertson_baseline(
        y0, tvec, rtol, atol, use_jacobian=True
    )
    print(meta_baseline)

    result_0, meta_0 = wrapper.solve_fast_robertson_0(y0, tvec, rtol, atol)
    print(meta_0)

    result_1, meta_1 = wrapper.solve_fast_robertson_1(y0, tvec, rtol, atol)
    print(meta_1)

    result_2, meta_2 = wrapper.solve_fast_robertson_2(y0, tvec, rtol, atol)
    print(meta_2)

    result_3, meta_3 = wrapper.solve_fast_robertson_0(
        y0, tvec, rtol, atol, enable_fast_solver=0
    )
    print(meta_3)

    assert (
        np.max(np.abs(result_baseline[1:] - result_0[1:]) / result_baseline[1:]) < 1e-4
    )
    assert (
        np.max(np.abs(result_baseline[1:] - result_1[1:]) / result_baseline[1:]) < 1e-4
    )
    assert (
        np.max(np.abs(result_baseline[1:] - result_2[1:]) / result_baseline[1:]) < 1e-4
    )
    assert (
        np.max(np.abs(result_baseline[1:] - result_3[1:]) / result_baseline[1:]) < 1e-4
    )


def test_compare_lsoda(tmpdir):
    """example problem from lsoda.f source code"""

    t, y1, y2, y3 = symbols("t y1 y2 y3")

    ydot1 = -0.04 * y1 + 1e4 * y2 * y3
    ydot3 = 3e7 * y2 * y2
    ydot2 = -ydot1 - ydot3

    # we change order of original system of odes to enforce permutations during modified
    # lsoda solver:
    ode_0 = OdeFast(
        "robertson_split", t, [y3, y2, y1], [ydot3, ydot2, ydot1], splits=[1]
    )
    ode_1 = OdeFast("robertson_nonsplit", t, [y3, y2, y1], [ydot3, ydot2, ydot1])
    ode_2 = Ode("robertson", t, [y3, y2, y1], [ydot3, ydot2, ydot1])

    module = Module()
    module.add(ode_0)
    module.add(ode_1)
    module.add(ode_2)

    tvec = 0.4 * 10 ** np.arange(0, 6)
    rtol = 1e-6
    atol = np.array([1e-8, 1e-10, 1e-8])

    root_folder = tmpdir.join("root_folder").strpath
    lsoda_folder = tmpdir.join("lsoda").strpath

    wrapper = module.compile_and_load(
        root_folder=root_folder, lsoda_folder=lsoda_folder
    )
    wrapper.set_sec_factor(1.0)

    y0 = np.array([0, 0, 1.0])
    result_fast_split, meta = wrapper.solve_fast_robertson_split(y0, tvec, rtol, atol)
    assert meta["new_traces"] == {}
    assert sum(meta["steps"]) > 0
    assert meta["istate"] > 0, meta

    result_fast_nonsplit, meta = wrapper.solve_fast_robertson_nonsplit(
        y0, tvec, rtol, atol
    )
    assert meta["new_traces"] == {0: [[1, 1, 2]]}
    assert sum(meta["steps"]) > 0
    assert meta["istate"] > 0, meta

    result, _ = wrapper.solve_robertson(y0, tvec, rtol, atol, use_jacobian=True)

    assert np.allclose(result_fast_split, result)
    assert np.allclose(result_fast_nonsplit, result)
    assert np.allclose(result_fast_nonsplit, result_fast_split)

    wrapper_path_before = wrapper.__file__

    wrapper = module.recompile_and_load(
        root_folder=root_folder, lsoda_folder=lsoda_folder
    )
    assert wrapper_path_before != wrapper.__file__

    result_fast_nonsplit, meta = wrapper.solve_fast_robertson_nonsplit(
        y0, tvec, rtol, atol
    )
    assert meta["new_traces"] == {}
    assert sum(meta["steps"]) > 0
    assert meta["istate"] > 0, meta

    assert np.allclose(result_fast_nonsplit, result)
    assert np.allclose(result_fast_nonsplit, result_fast_split)

    wrapper_path_before = wrapper.__file__
    w2 = module.recompile_and_load(root_folder=root_folder, lsoda_folder=lsoda_folder)
    assert wrapper_path_before == w2.__file__


def test_with_time_var_in_rhs(compile_and_load):
    x, t, a = symbols("x t a")

    ode_0 = OdeFast("test_0", t, [x], [a * t / x])
    ode_1 = Ode("test_1", t, [x], [a * t / x])
    module = Module()
    module.add(Globals(a))
    module.add(ode_0)
    module.add(ode_1)

    wrapper = compile_and_load(module)

    tvec = np.linspace(1, 20, 21)
    a = 1
    y0 = np.array((20.0,))
    wrapper.globals.a = a
    result_1, meta_1 = wrapper.solve_test_1(y0, tvec, 1e-4, 1e-4)

    assert meta_1["istate"] > 0

    result_0, meta_0 = wrapper.solve_fast_test_0(y0, tvec, 1e-4, 1e-4)
    assert meta_0["istate"] > 0

    assert meta_0["new_traces"] == {}
    assert sum(meta_0["steps"]) > 0

    assert np.allclose(result_1, result_0)


def test_vector_symbols(compile_and_load):
    state = Vector("s", 2)
    t = Symbol("t")

    # solution of this ode are sums of sin and cos, depending on the starting values
    lhs = [state[0], state[1]]
    rhs = [state[1], -state[0]]

    ode = OdeFast("wave", t, lhs, rhs)
    module = Module()
    module.add(ode)

    wrapper = compile_and_load(module)
    assert wrapper is not None

    t = np.linspace(0, 6, 10)

    result, meta = wrapper.solve_fast_wave(np.array([0.0, 1.0]), t, 1e-10, 1e-10)
    assert meta["new_traces"] == {}
    assert sum(meta["steps"]) > 0

    assert np.allclose(result[:, 0], np.sin(t))
    assert np.allclose(result[:, 1], np.cos(t))


def test_with_integral_and_interpolation(compile_and_load):
    x, tau, t = symbols("x tau t")
    squared = InterpolationFunction1D("squared")
    exp_as_integral = Integral(sp.exp(tau), tau, 0, t) + 1

    lhs = symbols("y1 y2")
    rhs = [lhs[1] / exp_as_integral, lhs[0] / squared(t)]
    ode = OdeFast("mixed", t, lhs, rhs)

    module = Module()
    module.add(ode)

    wrapper = compile_and_load(module)

    tvec = np.linspace(0, 4, 100)

    wrapper.set_squared_values(tvec, tvec**2)

    module2 = Module()
    module2.add(ode)
    module2.add(Function("squared", squared(x), x))
    module2.add(Function("exp", exp_as_integral, t))

    compile_and_load(module2)


def test_with_integral_with_cse_issue(compile_and_load):
    q = Symbol("q")
    t = Symbol("t")

    integrand = q**2 + q**4 + q**6
    ii = Integral(integrand * integrand, q, 0, 1)
    jj = Integral(integrand * q, q, 0, 1)

    lhs = (u, v) = symbols("u v")
    rhs = [ii * u + v, jj * v + u]

    f = Function("f", [ii, jj])
    g = Function("g", [ii, jj])

    ode = OdeFast("mixed", t, lhs, rhs)

    module = Module()
    module.add(ode)
    module.add(f)
    module.add(g)

    compile_and_load(module)


def test_highdim_ode(tmpdir):
    state = list(Vector("y", 100))
    (t,) = symbols("t")
    rhs = [-yi + yin for yi, yin in zip(state, state[1:] + state[:1])]
    ode = OdeFast("large", t, state, rhs)

    module = Module()
    module.add(ode)

    root_folder = tmpdir.join("root_folder").strpath
    lsoda_folder = tmpdir.join("lsoda").strpath

    wrapper = module.compile_and_load(
        root_folder=root_folder, lsoda_folder=lsoda_folder
    )

    y0 = np.arange(100) / 99.0
    tvec = np.linspace(0, 5, 100)

    solution, meta = wrapper.solve_fast_large(y0, tvec, atol=1e-5, rtol=1e-5)
    assert meta["istate"] == 2


def test_reordering_rows(tmpdir):
    t, y0, y1, y2, y3, y4, y5 = symbols("t y0 y1 y2 y3 y4 y5")

    lhs = [y0, y1, y2]

    ydot0 = -0.04 * y0 + 1e4 * y1 * y2
    ydot2 = 3e7 * y1 * y1
    ydot1 = -ydot0 - ydot2

    rhs = [ydot0, ydot1, ydot2]

    y0_vec = [1.0, 0.0, 0.0]
    atol = [1e-8, 1e-8, 1e-10]
    rtol = 1e-6

    ode_robertson = OdeFast("robertson", t, lhs, rhs)

    lhs_extended = [y0, y1, y2, y3, y4, y5][::-1]

    ydot3 = -0.04 * y3 + 1e4 * y4 * y5
    ydot5 = 3e7 * y4 * y4
    ydot4 = -ydot3 - ydot5

    rhs_extended = [ydot0, ydot1, ydot2, ydot3, ydot4, ydot5][::-1]
    atol_extended = (atol + atol)[::-1]
    y0_vec_extended = (y0_vec + y0_vec)[::-1]

    ode_baseline = OdeFast("baseline", t, lhs_extended, rhs_extended)
    ode_reordered = OdeFast("reordered", t, lhs_extended, rhs_extended, reorder=True)
    ode_reordered_with_splits = OdeFast(
        "reordered_with_splits", t, lhs_extended, rhs_extended, reorder=True, splits=[4]
    )

    module = Module()
    module.add(ode_robertson)
    module.add(ode_baseline)
    module.add(ode_reordered)
    module.add(ode_reordered_with_splits)

    root_folder = tmpdir.join("root_folder").strpath
    lsoda_folder = tmpdir.join("lsoda").strpath

    wrapper = module.compile_and_load(
        root_folder=root_folder, lsoda_folder=lsoda_folder
    )

    tvec = 0.4 * 10 ** np.arange(0, 6)

    result_robertson, meta_robertson = wrapper.solve_fast_robertson(
        np.array(y0_vec), tvec, rtol=rtol, atol=np.array(atol)
    )

    result_reordered, meta_reordered = wrapper.solve_fast_reordered(
        np.array(y0_vec_extended),
        tvec,
        rtol=rtol,
        atol=np.array(atol_extended),
    )

    (
        result_reordered_with_splits,
        meta_reordered_with_splits,
    ) = wrapper.solve_fast_reordered_with_splits(
        np.array(y0_vec_extended),
        tvec,
        rtol=rtol,
        atol=np.array(atol_extended),
    )

    result_baseline, meta_baseline = wrapper.solve_fast_baseline(
        np.array(y0_vec_extended),
        tvec,
        rtol=rtol,
        atol=np.array(atol_extended),
    )

    assert np.allclose(result_baseline[:, :2:-1], result_robertson)
    assert np.allclose(result_baseline, result_reordered)
    assert np.allclose(result_baseline, result_reordered_with_splits)

    assert np.allclose(
        wrapper.reordered_dot(1.0, np.arange(6.0)),
        wrapper.baseline_dot(1.0, np.arange(6.0)),
    )
