#!/usr/bin/env python
from numba import njit

from sympy2c import Function, Module, symbols


def test_numba(compile_and_load):
    a, b, c, d, e = symbols("a b c d e")

    m = Module()
    f = Function("f", a + b, a, b)
    g = Function("g", a**2, a)
    m.add(f)
    m.add(g)

    w = compile_and_load(m)
    f = w.f
    g = w.g

    assert g(1.0) == 1.0
    assert f(1.0, 2.0) == 3.0

    @njit
    def compute():
        return f(1.0, 2.0) + g(3.0)

    assert compute() == 12.0
