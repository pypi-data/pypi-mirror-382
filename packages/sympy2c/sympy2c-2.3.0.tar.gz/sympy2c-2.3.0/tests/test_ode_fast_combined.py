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

from sympy2c import Globals, Module, OdeCombined, symbols
from sympy2c.ode_fast import OdeFast


def test_combined_ode(tmpdir, compile_and_load):
    t, y0, y1, y2, st = symbols("t y0 y1 y2 st")

    ydot0 = -0.04 * y0 + 1e4 * y1 * y2
    ydot2 = 3e7 * y1 * y1
    ydot1 = -ydot0 - ydot2

    lhs = [y2, y1, y0]
    rhs = [ydot2, ydot1, ydot0]

    y0_vec = np.array([0.0, 0.0, 1.0])
    atol = np.array([1e-10, 1e-8, 1e-8])
    rtol = 1e-6

    ode_robertson_1 = OdeFast("robertson_1", t, lhs, rhs, reorder=False)
    ode_robertson_1_reordered = OdeFast(
        "robertson_1_reordered", t, lhs, rhs, reorder=True
    )
    ode_robertson_2 = OdeFast("robertson_2", t, lhs[::-1], rhs[::-1], reorder=False)

    tvec = 0.4 * 10 ** np.arange(0, 6)

    g = Globals(st)
    # f = Function("f", st)

    def switch_time(wrapper, a):
        st = wrapper.globals.st
        print("st = ", st)
        return st

    def switch(wrapper, t, y):
        return y[-1, ::-1]

    def merge(wrapper, tvec_0, t_switch, tvec_1, ys_0, ys_1):
        return np.vstack((ys_0, ys_1[:, ::-1]))

    ode_final = OdeCombined(
        "ode_final",
        ode_robertson_1,
        ode_robertson_2,
        switch_time,
        switch,
        merge,
    )
    ode_final_reordered = OdeCombined(
        "ode_final_reordered",
        ode_robertson_1_reordered,
        ode_robertson_2,
        switch_time,
        switch,
        merge,
    )
    module = Module()
    module.add(g)
    module.add(ode_robertson_1)
    module.add(ode_robertson_1_reordered)
    module.add(ode_robertson_2)
    module.add(ode_final)
    module.add(ode_final_reordered)
    # module.add(f)
    w = compile_and_load(module)

    w.globals.st = 400

    result_0, meta_0 = w.solve_fast_ode_final(y0_vec, tvec, rtol, atol)
    result_1, meta_1 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)
    result_2, meta_2 = w.solve_fast_ode_final_reordered(y0_vec, tvec, rtol, atol)
    assert np.allclose(result_0, result_1)
    assert np.allclose(result_0, result_2)
    assert meta_0.keys() == meta_1.keys()

    print(meta_0)
    print(meta_1)
    print(meta_2)

    w.globals.st = 401

    result_0, meta_0 = w.solve_fast_ode_final(y0_vec, tvec, rtol, atol)
    result_1, meta_1 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)
    assert np.allclose(result_0, result_1)
    assert meta_0.keys() == meta_1.keys()

    w.globals.st = 1e222

    result_0, meta_0 = w.solve_fast_ode_final(y0_vec, tvec, rtol, atol)
    result_1, meta_1 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)

    w.globals.st = -10
    result_2, meta_2 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)

    w.globals.st = tvec[0]
    result_3, meta_3 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)

    w.globals.st = tvec[0] - 1
    result_4, meta_4 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)

    w.globals.st = tvec[-1]
    result_5, meta_5 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)

    w.globals.st = tvec[-1] + 1
    result_6, meta_6 = w.solve_fast_robertson_1(y0_vec, tvec, rtol, atol)

    assert np.allclose(result_0, result_1, atol=0)
    assert np.allclose(result_0, result_2, atol=0)
    assert np.allclose(result_0, result_3, atol=0)
    assert np.allclose(result_0, result_4, atol=0)
    assert np.allclose(result_0, result_5, atol=0)
    assert np.allclose(result_0, result_6, atol=0)

    assert meta_0.keys() == meta_1.keys()
    assert meta_0.keys() == meta_2.keys()
    assert meta_0.keys() == meta_3.keys()
    assert meta_0.keys() == meta_4.keys()
    assert meta_0.keys() == meta_5.keys()
    assert meta_0.keys() == meta_6.keys()


def test_combined_ode_different_dimensions(tmpdir, compile_and_load):
    t, y0, y1, y2, y3, st = symbols("t y0 y1 y2 y3 st")

    ydot0 = -0.04 * y0 + 1e4 * y1 * y2
    ydot2 = 3e7 * y1 * y1
    ydot1 = -ydot0 - ydot2
    ydot3 = y3

    lhs = [y0, y1, y2, y3]
    rhs = [ydot0, ydot1, ydot2, ydot3]

    y0_vec = np.array([1.0, 0.0, 0.0, 0.0])
    atol = 1e-10  # np.array([1e-10, 1e-8, 1e-8])
    rtol = 1e-6

    ode_full = OdeFast("ode_full", t, lhs, rhs, reorder=False)
    ode_3 = OdeFast("ode_3", t, lhs[:3], rhs[:3], reorder=False)

    tvec = 0.4 * 10 ** np.arange(0, 6)

    g = Globals(st)

    def switch_time(wrapper, a):
        st = wrapper.globals.st
        return st

    def switch_1(wrapper, t, y):
        if not y.shape[0]:
            return y[:, :-1]
        return y[-1, :-1]

    def merge_1(wrapper, tvec_0, t_switch, tvec_1, ys_0, ys_1):
        if not ys_0.shape[0]:
            return ys_1
        return np.vstack((ys_0[:, :-1], ys_1))

    ode_final_1 = OdeCombined(
        "ode_final_1",
        ode_full,
        ode_3,
        switch_time,
        switch_1,
        merge_1,
    )

    def switch_2(wrapper, t, y):
        return np.append(y[-1], 0.0)

    def merge_2(wrapper, tvec_0, t_switch, tvec_1, ys_0, ys_1):
        if not ys_1.shape[1]:
            return ys_0
        return np.vstack((ys_0, ys_1[:, :-1]))

    ode_final_2 = OdeCombined(
        "ode_final_2",
        ode_3,
        ode_full,
        switch_time,
        switch_2,
        merge_2,
    )

    module = Module()
    module.add(g)
    module.add(ode_3)
    module.add(ode_full)
    module.add(ode_final_1)
    module.add(ode_final_2)
    w = compile_and_load(module)

    for st in (400, tvec[0], tvec[0] - 1, tvec[-1], tvec[-1] + 1):
        w.globals.st = st

        result_1, meta_1 = w.solve_fast_ode_final_1(y0_vec, tvec, rtol, atol)
        result_2, meta_2 = w.solve_fast_ode_final_2(y0_vec[:-1], tvec, rtol, atol)

        assert np.all(result_1 == result_2)


def test_combined_ode_recompile(tmpdir, compile_and_load):
    t, y1, y2, y3 = symbols("t y1 y2 y3")

    ydot1 = -0.04 * y1 + 1e4 * y2 * y3
    ydot3 = 3e7 * y2 * y2
    ydot2 = -ydot1 - ydot3

    # we change order of original system of odes to enforce permutations during
    # modified lsoda solver:
    ode_1 = OdeFast("robertson_1", t, [y3, y2, y1], [ydot3, ydot2, ydot1])
    ode_2 = OdeFast("robertson_2", t, [y3, y2, y1], [ydot3, ydot2, ydot1])

    def switch_time(wrapper, a):
        return 401

    def switch(wrapper, t, y):
        return y[-1, :]

    def merge(wrapper, tvec_0, t_switch, tvec_1, ys_0, ys_1):
        return np.vstack((ys_0, ys_1))

    ode_combined = OdeCombined(
        "robertson_combined", ode_1, ode_2, switch_time, switch, merge
    )

    module = Module()
    module.add(ode_1)
    module.add(ode_2)
    module.add(ode_combined)

    tvec = 0.4 * 10 ** np.arange(0, 6)
    rtol = 1e-6
    atol = np.array([1e-8, 1e-10, 1e-8])
    y0 = np.array([0, 0, 1.0])

    root_folder = tmpdir.join("root_folder").strpath
    lsoda_folder = tmpdir.join("lsoda").strpath

    w = module.compile_and_load(root_folder=root_folder, lsoda_folder=lsoda_folder)
    w.set_sec_factor(1.0)
    result_0, meta_0 = w.solve_fast_robertson_combined(y0, tvec, rtol, atol)

    assert w.get_new_traces("robertson_1") == {}
    assert w.get_new_traces("robertson_2") == {0: [[1, 1, 2]]}

    w = module.recompile_and_load(root_folder=root_folder, lsoda_folder=lsoda_folder)
    result_1, meta_1 = w.solve_fast_robertson_combined(y0, tvec, rtol, atol)
    assert w.get_new_traces("robertson_1") == {}
    assert w.get_new_traces("robertson_2") == {}

    assert np.all(result_0 == result_1)
