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


import pytest
import sympy

from sympy2c.rec_inv import rec_inv


@pytest.mark.parametrize(
    "n, m",
    [
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (3, 0),
        (3, 1),
        (3, 2),
        (3, 3),
        (3, 4),
        (3, 5),
        (4, 2),
    ],
)
def test_recinv(m, n):
    a, b, c = sympy.symbols("a b c")
    A = sympy.eye(n)
    for i in range(n - 1):
        A[i, i + 1] = a if i % 2 == 0 else a * b
        A[i + 1, i] = b if i % 2 == 0 else a * b + c
        # A[0, i] = b + c + 1

    B = sympy.zeros(m, n)
    D = sympy.eye(m)

    M = sympy.Matrix(sympy.BlockMatrix([[A, B.T], [B, D]]))

    xii, Mi = rec_inv(M)
    check = M * Mi
    while any(str(a).startswith("__x") for a in check.atoms()):
        check = check.subs(xii)
    assert sympy.simplify(check) == sympy.eye(m + n)
