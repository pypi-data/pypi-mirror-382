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

from hashlib import md5

import sympy as sp

from .utils import align, concat_generator_results
from .wrapper import WrapperBase


class InterpolationFunction1DInstance(
    sp.Function("_InterpolationFunction1D", nargs=2, real=True)
):
    @property
    def free_symbols(self):
        return self.argument.free_symbols

    @property
    def _name(self):
        return self.args[0]

    @property
    def argument(self):
        return self.args[1]

    def __hash__(self):
        return hash((self._name, self.argument))

    def __eq__(self, other):
        if type(self) != type(other):  # noqa: E721
            return False
        return self._name == other._name and self.argument == other.argument

    def __str__(self):
        return "{}({})".format(self._name, self.argument)

    def _subs(self, old, new, **hints):
        return InterpolationFunction1DInstance(
            self.args[0], self.args[1]._subs(old, new, **hints)
        )


class InterpolationFunction1D(
    sp.Function("_InterpolationFunction1D", nargs=1, real=True)
):
    @property
    def free_symbols(self):
        return {self}

    @property
    def _name(self):
        return self.args[0]

    def __hash__(self):
        return hash((self._name,))

    def __eq__(self, other):
        if type(self) != type(other):  # noqa: E721
            return False
        return self._name == other._name

    def __call__(self, argument):
        return InterpolationFunction1DInstance(self._name, argument)

    def get_unique_id(self):
        return md5(str(self._name).encode("utf-8")).hexdigest()

    def _subs(self, old, new, **hints):
        return InterpolationFunction1D(self.args[0]._subs(old, new, **hints))


class InterpolationFunction1DWrapper(WrapperBase):
    def __init__(self, interpolation_function_1d, visitor):
        # self.namejkjjk = interpolation_function_1d
        self.name = interpolation_function_1d._name
        self.visitor = visitor

    def setup_code_generation(self):
        pass

    def get_unique_id(self):
        return md5(str(self.name).encode("utf-8")).hexdigest()

    def c_header(self):
        return align(
            """
            |extern "C" {{
            |   void         _set_{name}_values(double *, double *, size_t);
            |}}
            |
            |extern "C" double __ip_{name}(double);
            |extern "C" void   __ip_sorted_{name}(double *, size_t, double *);
            |
            |extern "C" double  * _{name}_x_min_p, * _{name}_x_max_p;
            |extern "C" double  * _get_x_{name}();
            |extern "C" double  * _get_y_{name}();
            |extern "C" int _get_n_{name}();
            """.format(name=self.name)
        )

    def c_code(self, header_file_path):
        return align(
            """
            |gsl_interp_accel * {name}_interp_accel = 0;
            |gsl_spline       * {name}_spline = 0;
            |static double    _{name}_x_min, _{name}_x_max;
            |double           * _{name}_x_min_p = NULL, * _{name}_x_max_p = NULL;
            |static double    *_{name}_x = NULL, *_{name}_y;
            |static int       _{name}_n;
            |
            |extern "C" double * _get_x_{name}() {{
            |    return _{name}_x;
            |}}
            |
            |extern "C" double * _get_y_{name}() {{
            |    return _{name}_y;
            |}}
            |
            |extern "C" int _get_n_{name}() {{
            |    return _{name}_n;
            |}}
            |
            |extern "C" void _set_{name}_values(double *x, double *y, size_t n) {{
            |     if ({name}_interp_accel) {{
            |         gsl_spline_free({name}_spline);
            |         gsl_interp_accel_free({name}_interp_accel);
            |     }}
            |     {name}_interp_accel = gsl_interp_accel_alloc();
            |     if ({name}_interp_accel == 0) {{
            |          set_error_message_gsl("_set_{name}_values", GSL_ENOMEM);
            |          return;
            |     }}
            |     {name}_spline = gsl_spline_alloc(gsl_interp_cspline, n);
            |     if ({name}_spline == 0) {{
            |          set_error_message_gsl("_set_{name}_values", GSL_ENOMEM);
            |          return;
            |     }}
            |     gsl_spline_init({name}_spline, x, y, n);
            |
            |
            |     if (_{name}_x != NULL) {{
            |        free(_{name}_x);
            |        free(_{name}_y);
            |     }}
            |     _{name}_x = (double *)malloc(n * sizeof(double));
            |     _{name}_y = (double *)malloc(n * sizeof(double));
            |
            |     /* setting pointers to value different to NULL indicactes that
            |        this function was called: */
            |     _{name}_x_min = _{name}_x_max = x[0];
            |     _{name}_x[0] = x[0];
            |     _{name}_y[0] = y[0];
            |
            |     for (size_t i = 1; i < n; ++i)
            |     {{
            |         if (x[i] > _{name}_x_max) _{name}_x_max = x[i];
            |         if (x[i] < _{name}_x_min) _{name}_x_min = x[i];
            |         _{name}_x[i] = x[i];
            |         _{name}_y[i] = y[i];
            |     }}
            |     _{name}_n = n;
            |
            |     _{name}_x_min_p = & _{name}_x_min;
            |     _{name}_x_max_p = & _{name}_x_max;
            |
            |}}
            |
            |extern "C" double __ip_{name}(double x) {{
            |     double result = 0.0;
            |     int    error_code = 0;
            |     if ({name}_spline) {{
            |         if (x > _{name}_x_max) x = _{name}_x_max;
            |         error_code = gsl_spline_eval_e({name}_spline, x,
            |                                        {name}_interp_accel, &result);
            |         if (error_code)
            |              set_error_message_gsl("spline eval failed", error_code);
            |     }}
            |     else
            |         set_error_message("you must call set_{name}_values first");
            |     return result;
            |}}
            |
            |extern "C" void __ip_sorted_{name}(double *x, size_t n, double* y) {{
            |     if ({name}_spline) {{
            |         cspline_eval_vector_sorted({name}_spline->interp->state,
            |                                    {name}_spline->x,
            |                                    {name}_spline->y,
            |                                    {name}_spline->interp->size,
            |                                    x, n, y);
            |     }}
            |     else
            |         set_error_message("you must call set_{name}_values first");
            |}}
            """.format(name=self.name)
        )

    @concat_generator_results
    def cython_code(self, header_file_path):
        # we insert "_" at beginning of c functions to avoid clash with
        # cython functions:
        for code in self.cython_header(header_file_path):
            yield code
        for code in self.cython_function_wrapper():
            yield code
        return
        for code in self.cython_ufunc_wrapper():
            yield code

    def cython_header(self, header_file_path):
        yield align(
            """
        |cdef extern from "{header_file_path}":
        |    double __ip_{name}(double);
        |    void   __ip_sorted_{name}(double *, size_t, double *);
        |    double _set_{name}_values(double *, double *, size_t);
        |    double  * _{name}_x_min_p, * _{name}_x_max_p;
        |    double  * _get_x_{name}();
        |    double  * _get_y_{name}();
        |    int _get_n_{name}();
        """.lstrip().format(header_file_path=header_file_path, name=self.name)
        )

    def cython_function_wrapper(self):
        yield align(
            """
        |def set_{name}_values(np.ndarray[np.double_t, ndim=1, cast=True, mode="c"] x,
        |                      np.ndarray[np.double_t, ndim=1, cast=True, mode="c"] y):
        |
        |    assert len(x) == len(y), "x and y must be of same size"
        |    assert len(x) > 0, "empty array not allowed"
        |    _set_{name}_values(&x[0], &y[0], len(x))
        |
        |def ip_sorted_{name}(np.ndarray[np.double_t, ndim=1, cast=True] x):
        |    cdef result = np.zeros_like(x, np.float64)
        |    cdef double[:] _result = result
        |    cdef double[:] _x = x.ravel()
        |    __ip_sorted_{name}(&_x[0], x.shape[0], &_result[0])
        |    return result
        |
        |def get_x_{name}():
        |    if _get_x_{name}() == NULL:
        |       return None
        |    return np.asarray(<np.float64_t[:_get_n_{name}()]> _get_x_{name}())
        |
        |def get_y_{name}():
        |    if _get_x_{name}() == NULL:
        |       return None
        |    return np.asarray(<np.float64_t[:_get_n_{name}()]> _get_y_{name}())
        |
        """
        ).format(name=self.name)

    def determine_required_extra_wrappers(self):
        pass
