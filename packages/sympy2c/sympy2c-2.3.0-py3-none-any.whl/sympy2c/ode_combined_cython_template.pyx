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

def symbols_{id_}():
    return {symbols}



def solve_fast_{id_}(wrapper,
                     np.ndarray y0,
                     np.ndarray tvec,
                     rtol,
                     atol,
                     int max_iter=200000,
                     int max_order=5,
                     enable_fast_solver=1,
                     enable_sparse_lu_solver=1,
                     double h0=0.0,
                     ):

{switch_time_function_src}

{switch_function_src}

{merge_function_src}

    assert y0.ndim == 1, "y0 must be one-dimensional"
    assert tvec.ndim == 1, "tvec must be one-dimensional"

    cdef double t_switch = {switch_time_function_name}(wrapper, tvec)

    if tvec[0] < t_switch < tvec[-1]:
        tvec_0 = np.concatenate((tvec[tvec < t_switch], [t_switch]))
        tvec_1 = np.concatenate(([t_switch], tvec[tvec > t_switch]))
    elif tvec[-1] <= t_switch:
        tvec_0 = tvec
        tvec_1 = np.arange(0, dtype=tvec.dtype)
    else:
        tvec_0 = np.arange(0, dtype=tvec.dtype)
        tvec_1 = tvec

    n = y0.shape[0]

    if t_switch > tvec[0]:
        result_0, meta_0 = {solver_0}(wrapper, y0, tvec_0, rtol, atol, max_iter,
                                      max_order, enable_fast_solver,
                                      enable_sparse_lu_solver, h0)
        y0 = {switch_function_name}(wrapper, t_switch, result_0)
    else:
        result_0 = np.zeros((0, len(y0)), dtype=y0.dtype)
        meta_0 = dict(istate=2, num_steps=0, num_feval=0,
                    num_lu_solver_calls=0, last_switch_at=t_switch, seconds_needed=0.0,
                    total_time_fast_solver=0.0, total_time_lup_solver=0.0,
                    steps=[], step_sizes=[], new_traces=[], lu_call_counts=0,
                    )
        y0 = {switch_function_name}(wrapper, t_switch, y0.reshape(1, -1))

    # we always call solver_1 to make sure result_1 and meta_1 are populated,
    # might be that this solver does no single step
    if t_switch < tvec[-1]:
        result_1, meta_1 = {solver_1}(wrapper, y0, tvec_1, rtol, atol, max_iter,
                                      max_order, enable_fast_solver,
                                      enable_sparse_lu_solver, h0)

    else:
        result_1 = np.zeros((0, len(y0)), dtype=y0.dtype)
        meta_1 = dict(istate=2, num_steps=0, num_feval=0,
                     num_lu_solver_calls=0, last_switch_at=tvec[0], seconds_needed=0.0,
                     total_time_fast_solver=0.0, total_time_lup_solver=0.0,
                     steps=[], step_sizes=[], new_traces=[], lu_call_counts=0,
                     )

    meta = dict(istate=min(meta_0["istate"], meta_1["istate"]),
                num_steps=meta_0["num_steps"] + meta_1["num_steps"],
                num_feval=meta_0["num_feval"] + meta_1["num_feval"],
                num_lu_solver_calls=meta_0["num_lu_solver_calls"] + meta_1["num_lu_solver_calls"],
                last_switch_at=max(meta_0["last_switch_at"], meta_1["last_switch_at"]),
                seconds_needed=meta_0["seconds_needed"] + meta_1["seconds_needed"],
                total_time_fast_solver=meta_0["total_time_fast_solver"] + meta_1["total_time_fast_solver"],
                total_time_lup_solver=meta_0["total_time_lup_solver"] + meta_1["total_time_lup_solver"],
                steps=np.concatenate((meta_0["steps"], meta_1["steps"])),
                step_sizes=np.concatenate((meta_0["step_sizes"], meta_1["step_sizes"])),
                new_traces=[meta_0["new_traces"], meta_1["new_traces"]],
                lu_call_counts=[meta_0["lu_call_counts"], meta_1["lu_call_counts"]],
                )

    if t_switch < tvec[-1]:
        result_0 = result_0[:-1]
        tvec_0 = tvec_0[:-1]
    if t_switch not in tvec and t_switch > tvec[0]:
        result_1 = result_1[1:]
        tvec_1 = tvec_1[1:]

    return {merge_function_name}(wrapper, tvec_0, t_switch, tvec_1, result_0, result_1), meta
