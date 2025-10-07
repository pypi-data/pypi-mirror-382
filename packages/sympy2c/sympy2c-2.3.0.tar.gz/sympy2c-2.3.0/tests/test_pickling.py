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


import glob
import importlib
import inspect
import os
from pickle import dumps, loads

from sympy2c import (
    ERROR,
    Alias,
    Function,
    Globals,
    Integral,
    Module,
    Symbol,
    Vector,
    symbols,
)


def test_all_classes_with_own_new_method_for_pickling():
    """
    Pickling can fail if classes implement their own __new__ method.
    Here we extract all classes implemented in sympy2c and check if
    they have their own __new__ method implemented within sympy2c.
    For those classes we run tests.
    """

    import sympy2c

    folder = sympy2c.__path__[0]

    setup_functions = {
        "VectorElement": _setup_pickling_vector_element,
        "Vector": _setup_pickling_vector,
        "Symbol": _setup_pickling_symbol,
        "Integral": _setup_pickling_integral,
        "Function": _setup_pickling_function,
        "InternalFunction": None,
        "ERROR": _setup_pickling_error,
    }

    tested = set()

    for p in glob.glob(folder + "/**/*.py", recursive=True):
        # fix path relative to folder above sympy package:
        p = os.path.relpath(p, os.path.dirname(folder))

        # filepath to module notation:
        module_specificer = os.path.splitext(p)[0].replace("/", ".")
        module = importlib.import_module(module_specificer)

        for item in module.__dict__.values():
            if not inspect.isclass(item):
                continue

            if (getattr(item.__new__, "__module__") or "").startswith("sympy2c."):
                item_name = str(item)
                if item_name in tested:
                    continue
                tested.add(item_name)
                if "." in item_name:
                    # extract name from "<class ....."> notation.
                    # some classes derived from sympy.Function don't have this
                    # struture.
                    item_name = item_name.split("'")[1].split(".")[-1]
                if item_name not in setup_functions:
                    assert False, "no test function implemented for {}".format(
                        item_name
                    )
                value = setup_functions[item_name]
                if value is not None:
                    value2 = loads(dumps(value))
                    assert value == value2
                    if hasattr(value, "free_symbols"):
                        assert value.free_symbols == value2.free_symbols


def _setup_pickling_vector():
    return Vector("v", 10)


def _setup_pickling_vector_element():
    return Vector("v", 10)[0]


def _setup_pickling_integral():
    x = Symbol("x")
    ii = Integral(x**2, x, 0, 1)
    return ii


def _setup_pickling_function():
    x = Symbol("x")
    f = Function("f", x * x, x)
    return f


def _setup_pickling_symbol():
    x = Symbol("x")
    return x


def _setup_pickling_error():
    e = ERROR("message")
    return e


def test_pickling_module_and_wrapper(compile_and_load):
    s = Symbol("s")
    t = Symbol("t")

    f = Function("f", s * t, s)
    g = Globals(t)

    m = Module()
    m.add(g)
    m.add(f)

    assert loads(dumps(m)).get_unique_id() == m.get_unique_id()

    w = compile_and_load(m)

    w_back = loads(dumps(w))

    w.globals.t = 2
    w_back.globals.t = 2

    assert w.f(3) == w_back.f(3) == 6


def test_pickling_function_with_alias():
    u, v, w = symbols("u v w")
    y = Alias("y", u, v, w)
    f = Function("y", u, y)

    f_back = loads(dumps(f))
    assert f_back.aliases == f.aliases
