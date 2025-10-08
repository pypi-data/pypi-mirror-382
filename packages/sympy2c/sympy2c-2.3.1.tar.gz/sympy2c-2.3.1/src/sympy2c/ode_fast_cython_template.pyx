# This file is part of sympy2c.
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


cdef extern from "<array>" namespace "std" nogil:
    cdef cppclass array{N} "std::array<int, {N}> ":
        array{N}() except+
        int& operator[](size_t)


cdef extern:
    void _rhs_{id_}(long * n, double * t, double * y, double * ydot)
    void _fnorm_{id_}(double * ewt, double *y)
    void _solve_fast_{id_}(double *t, double *x, double *y, int *, int)
    void _reset_next_solver_{id_}()
    void _reset_timers_{id_}()
    double _get_timer_{id_}_fast()
    double _get_timer_{id_}_lup()
    void _enable_fast_solver_{id_}(int)
    void _enable_sparse_lu_solver_{id_}(int)
    vector[vector[unsigned int]] _call_counts_{id_};


def solve_fast_lu_{id_}(double t, double[:] x, double[:] y):
    cdef int ier, i

    # copying is important as solvers will overwrite y:
    cdef np.ndarray data = np.array(y).copy()
    cdef double[:] data_view = data
    _solve_fast_{id_}(&t, &data_view[0], &data_view[0], &ier, 0)
    x[:] = data_view


def symbols_{id_}():
    return {symbols}


@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def {id_}_dot(double lna,  double[:] y0):
    cdef np.ndarray result = np.zeros(({N},))
    cdef double [:] result_view = result
    cdef long n = {N}
    cdef double y_permuted[{N}]
    cdef double permuted_result[{N}]
    cdef int[{N}] permutation = [{permutation}]
    for j in range({N}):
        y_permuted[j] = y0[permutation[j]]
    _rhs_{id_}(&n, &lna, &y_permuted[0], &permuted_result[0])
    for j in range({N}):
        result_view[permutation[j]] = permuted_result[j]
    return result




@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
cpdef solve_fast_{id_}(
                     wrapper,
                     double[:] y0,
                     double[:] tvec,
                     rtol,
                     atol,
                     int max_iter=200000,
                     int max_order=5,
                     int enable_fast_solver=1,
                     int enable_sparse_lu_solver=1,
                     double h0=0.0,
                     ):


    assert isinstance(atol, (float, np.ndarray)), "atol must be number or numpy array"
    assert 1 <= max_order <= 5, "max_order must be in the range 1..5"

    if isinstance(atol, float):
        atol = atol * np.ones(({N},))

    if isinstance(rtol, float):
        rtol = rtol * np.ones(({N},))

    assert atol.shape == ({N},), "atol must be either a number of a vector of length {N}"
    assert rtol.shape == ({N},), "rtol must be either a number of a vector of length {N}"

    cdef int[{N}] permutation = [{permutation}]
    cdef long int neq = {N}
    cdef double __y[{N}], t, tout
    cdef int i, j
    cdef double[:] y = np.zeros(({N},))

    cdef double _atol[{N}]
    cdef double _rtol[{N}]

    for i in range({N}):
        y[i] = y0[permutation[i]]
        _atol[i] = atol[permutation[i]]
        _rtol[i] = rtol[permutation[i]]

    cdef int nt = tvec.shape[0]
    cdef double tmax = tvec[nt - 1]

    cdef double rwork[{LRW}]

    cdef long int itask = 4  # dont overshoot tcrit = rwork[0]
    rwork[0] = tmax

    cdef long int istate = 1  # must be set like this
    cdef long int iopt = 1  # optional inputs in rwork/iwork

    cdef long int itol = 4  # provide rtol and atol as vector

    cdef long int lrw = {LRW}
    cdef double lasty[{N}]

    cdef long int liw = {LIW}
    cdef long int iwork[{LIW}]
    cdef long int jt = 4  # user supplied jacobian sparse

    for i in range(liw):
        iwork[i] = 0

    for i in range(lrw):
        rwork[i] = 0.0


    # tcrit
    rwork[0] = tvec[nt - 1]
    rwork[4] = h0

    iwork[0] = iwork[1] = 0  # bandwidth sparse matrix

    iwork[5] = max_iter    # iwork(6) in fortran
    iwork[8] = max_order   # iwork(9) in fortran, max order of bdf

    cdef np.ndarray result = np.zeros((nt, {N}), order="C")
    cdef double [:, ::1] result_view = result

    cdef np.ndarray steps = np.zeros((nt,), dtype=np.uint32)
    cdef np.uint32_t [:] steps_view = steps

    result_view[0, :] = y0

    cdef long started = microtime()

    cdef int last_steps = 0

    _reset_next_solver_{id_}()
    _enable_fast_solver_{id_}(enable_fast_solver)
    _enable_sparse_lu_solver_{id_}(enable_sparse_lu_solver)
    _reset_timers_{id_}()

    _call_counts_{id_}.clear()

    cdef vector[double] hvalues_c = vector[double]()
    cdef long handle = id(list())  # random key
    _hvalues[handle] = &hvalues_c


    with nogil:
        for i in range(1, nt):
            t = tvec[i - 1]
            tout = tvec[i]

            lsodafast_(<S_fp>_rhs_{id_}, NULL, &neq, &y[0], &t, &tout, &itol, _rtol, _atol, &itask,
                &istate, &iopt, rwork, &lrw, iwork, &liw, NULL, &jt, <V_fp>_solve_fast_{id_},
                <D_fp>_fnorm_{id_}, <V_fp> _hvalue_callback, &handle)

            if istate <= 0:
                break

            for j in range({N}):
                result_view[i, permutation[j]] = y[j]

            steps_view[i] = iwork[10] - last_steps
            last_steps = iwork[10]
            iwork[10] = 0
            # step_sizes_view[i] = ls0001_.h

    cdef needed = microtime() - started

    step_sizes = []
    cdef vector[double].iterator it = hvalues_c.begin()
    while it != hvalues_c.end():
        step_sizes.append(deref(it))
        inc(it)

    _hvalues.erase(_hvalues.find(handle))

    new_traces = get_new_traces("{id_}")
    if new_traces:
        update_new_traces("{ode_id}", new_traces)

    result_meta = dict(istate=istate,
                       num_steps=iwork[10],
                       num_feval=iwork[11],
                       num_lu_solver_calls=iwork[12],
                       last_switch_at=rwork[14],
                       seconds_needed = needed/1e6,
                       steps=steps,
                       step_sizes=step_sizes,
                       new_traces=new_traces,
                       total_time_fast_solver=_get_timer_{id_}_fast(),
                       total_time_lup_solver=_get_timer_{id_}_lup(),
                       lu_call_counts=_call_counts_{id_},
                       )

    return result, result_meta
