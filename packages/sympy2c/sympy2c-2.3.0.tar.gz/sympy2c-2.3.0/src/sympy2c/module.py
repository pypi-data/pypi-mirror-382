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

import sys
from functools import partial

from .compiler import LoadedModule, build_folder, compile_if_needed_and_load
from .create_curry_class import create_interface_onary
from .utils import Hasher, align, concat_generator_results
from .wrapper import WrapperBase


def _print_code_fragment(code, line_no, e, stream=sys.stderr, extra_lines=5):
    for i, line in enumerate(code.split("\n"), 1):
        if i < line_no - extra_lines or i > line_no + extra_lines:
            continue
        if i == line_no:
            print(">>>", str(e) + ":", file=stream)
        print("{:3d}".format(i), line.rstrip(), file=stream)


class Module(object):
    def __init__(self):
        from .globals import Globals

        self.globals_ = Globals()
        self.functions = []
        self.python_functions = []
        self.odes = []
        self.fast_odes = []
        self.combined_odes = []
        self._reset_unique_id()

    def _reset_unique_id(self):
        self._unique_id = None

    def add(self, what):
        from .function import Function
        from .globals import Globals
        from .ode import Ode
        from .ode_combined import OdeCombined
        from .ode_fast import OdeFast
        from .python_function import PythonFunction

        self._reset_unique_id()
        if isinstance(what, Function):
            self._add_function(what)
        elif isinstance(what, Globals):
            self._add_globals(what)
        elif isinstance(what, Ode):
            self._add_ode(what)
        elif isinstance(what, OdeFast):
            self._add_ode_fast(what)
        elif isinstance(what, OdeCombined):
            self._add_ode_combined(what)
        elif isinstance(what, PythonFunction):
            self._add_python_function(what)
        else:
            raise ValueError("don't know how to add {!r}".format(what))

    def get_unique_id(self):
        if self._unique_id is None:
            md5 = Hasher()
            for di in self.functions:
                md5.update(di._name, di.get_unique_id())
            for di in self.odes:
                md5.update(di.name, di.get_unique_id())
            for di in self.fast_odes:
                md5.update(di.name, di.get_unique_id())
            for di in self.combined_odes:
                md5.update(di.name, di.get_unique_id())
            for di in self.python_functions:
                md5.update(di.name, di.get_unique_id())

            from . import __version__

            md5.update("globals", self.globals_.get_unique_id())
            version = "_".join(map(str, __version__))
            self._unique_id = version + "_" + md5.hexdigest()
        return self._unique_id

    def _add_function(self, f):
        common = set(self.globals_) & set(f.arguments)
        assert not common, "symbols(s) {} already declared as globals".format(
            ", ".join(map(str, common))
        )
        self.functions.append(f)

    def _add_ode(self, ode):
        self.odes.append(ode)

    def _add_ode_fast(self, ode):
        self.fast_odes.append(ode)

    def _add_ode_combined(self, ode):
        self.combined_odes.append(ode)

    def _add_python_function(self, f):
        self.python_functions.append(f)

    def _add_globals(self, globals_):
        for symbol in globals_.variables:
            self.globals_.add_variable(symbol)

    @staticmethod
    def _setup_ns():
        m = Module()

        def add_function(name, expression, *args):
            f = Function(name, expression, *args)
            m.add(f)
            return f

        def add_ode(name, tvar, lhs, rhs, **kw):
            ode = Ode(name, tvar, lhs, rhs, **kw)
            m.add(ode)
            return ode

        def add_ode_fast(name, tvar, lhs, rhs, **kw):
            ode = OdeFast(name, tvar, lhs, rhs, **kw)
            m.add(ode)
            return ode

        def add_ode_combined(*a, **kw):
            ode = OdeCombined(*a, **kw)
            m.add(ode)
            return ode

        def decl(*names, ns=None):
            for name in names:
                exec("{name} = Symbol('{name}')".format(name=name), ns)

        from .expressions import Max, Min, isnan
        from .function import Alias, Function
        from .integral import ERROR, Checked, IfThenElse, Integral
        from .interpolation import InterpolationFunction1D
        from .ode import Ode
        from .ode_combined import OdeCombined
        from .ode_fast import OdeFast
        from .symbol import Symbol
        from .vector import Vector

        ns = {
            "Function": add_function,
            "Integral": Integral,
            "InterpolationFunction1D": InterpolationFunction1D,
            "Symbol": Symbol,
            "Alias": Alias,
            "Min": Min,
            "Max": Max,
            "isnan": isnan,
            "Vector": Vector,
            "IfThenElse": IfThenElse,
            "ERROR": ERROR,
            "Checked": Checked,
            "Ode": add_ode,
            "OdeFast": add_ode_fast,
            "OdeCombined": add_ode_combined,
            "globals_": [],
        }
        return ns, decl, m

    @staticmethod
    def load_sympy_code(path, locals_=None):
        if locals_ is None:
            locals_ = {}

        ns, decl, _ = Module._setup_ns()
        __builtins__.update(ns)
        __builtins__["decl"] = partial(decl, ns=__builtins__)
        __builtins__.update(locals_)
        import importlib
        import os

        try:
            sys.path.insert(0, os.path.dirname(path))
            importlib.__import__(os.path.basename(path)[:-3], globals(), ns)
        finally:
            del sys.path[0]

    @staticmethod
    def parse_sympy_code(code, locals_=None):
        from .globals import Globals

        if locals_ is None:
            locals_ = {}

        ns, decl, m = Module._setup_ns()
        ns["decl"] = partial(decl, ns=ns)

        ns.update(locals_)

        try:
            exec(code, ns)
        except Exception as e:
            tb = sys.exc_info()[-1]
            tb_next = tb.tb_next
            if tb_next is not None:
                line_no = tb_next.tb_lineno
                _print_code_fragment(code, line_no, e)
            raise e
        globals_ = ns["globals"]
        m.add(Globals(*globals_))

        return m, ns

    @staticmethod
    def parse_sympy_file(path, locals_=None):
        with open(path, "r") as fh:
            return Module.parse_sympy_code(fh.read(), locals_)

    def get_module_wrapper(self):
        return ModuleWrapper(self)

    def compile_and_load(
        self,
        root_folder=None,
        lsoda_folder=None,
        gsl_root=None,
        compilation_flags=None,
    ):
        wrapper = ModuleWrapper(self)
        wrapper.setup_wrappers(True, None)
        return wrapper.compile_and_load(
            root_folder, lsoda_folder, gsl_root, compilation_flags
        )

    def recompile_and_load(
        self,
        root_folder=None,
        lsoda_folder=None,
        gsl_root=None,
        compilation_flags=None,
        force=False,
    ):
        from .ode_fast import read_known_traces, read_new_traces, write_known_traces

        found_new_traces = False
        for ode in self.fast_odes:
            N = len(ode.rhs)
            splits = ode.splits
            uid = ode.get_unique_id()
            latest_traces = read_known_traces(uid)
            new_traces = read_new_traces(uid)
            if not new_traces:
                continue
            if not latest_traces:
                sizes = (
                    s
                    for s in [splits[0]]
                    + [s1 - s0 for (s0, s1) in zip(splits, splits[1:])]
                    + [N - splits[-1]]
                    if s
                )
                latest_traces = {i: [list(range(s))] for i, s in enumerate(sizes)}
            for level, traces in new_traces.items():
                for trace in traces:
                    if trace not in latest_traces[level]:
                        latest_traces[level].append(trace)
                        found_new_traces = True
            write_known_traces(uid, latest_traces)
        if force or found_new_traces:
            return self.compile_and_load(
                root_folder, lsoda_folder, gsl_root, compilation_flags
            )
        else:
            wrapper = ModuleWrapper(self)
            wrapper.setup_wrappers(True, None)
            return LoadedModule(build_folder(wrapper, compilation_flags, root_folder))


class ModuleWrapper(WrapperBase):
    def __init__(self, module):
        from . import __version__

        self.__version__ = (
            __version__
        )  # for correct caching of generated and compiled code
        self.functions = module.functions
        self.globals_ = module.globals_
        self.odes = module.odes[:]
        self.fast_odes = module.fast_odes[:]
        self.combined_odes = module.combined_odes[:]
        self.python_functions = module.python_functions[:]

        from .visitor import Sp2CVisitor

        self.visitor = Sp2CVisitor(self.globals_)

        self.function_wrappers = None
        self.ode_wrappers = None
        self.fast_ode_wrappers = None
        self._unique_id_0 = None
        self._unique_id = None

    def setup_wrappers(self, compile_fast_odes=False, traces=None):
        from .function import function_wrapper_factory

        self.function_wrappers = [
            function_wrapper_factory(function, self.globals_, self.visitor)
            for function in self.functions
        ]
        self.ode_wrappers = [
            ode.wrapper(ode, self.globals_, self.visitor) for ode in self.odes
        ]

        self.combined_ode_wrappers = [
            ode.wrapper(ode, self.globals_, self.visitor) for ode in self.combined_odes
        ]

        self.python_function_wrappers = [f.wrapper() for f in self.python_functions]

        if traces is None:
            traces = {}

        if compile_fast_odes:
            self.fast_ode_wrappers = [
                ode.wrapper(ode, self.globals_, self.visitor, traces.get(ode.name))
                for ode in self.fast_odes
            ]
        else:
            self.fast_ode_wrappers = []

        for w in self.function_wrappers + self.ode_wrappers + self.fast_ode_wrappers:
            w.determine_required_extra_wrappers()

        return self

    def setup_code_generation(self):
        for wrapper in (
            self.function_wrappers
            + self.ode_wrappers
            + self.fast_ode_wrappers
            + self.combined_ode_wrappers
            + self.python_function_wrappers
            + list(self.visitor.extra_wrappers.values())
        ):
            wrapper.setup_code_generation()

    def get_unique_id(self):
        if self.function_wrappers is None:
            raise RuntimeError("you must first call setup_wrappers()")

        if self._unique_id is not None:
            return self._unique_id

        if self._unique_id_0 is None:
            md5 = Hasher()
            for di in (
                self.function_wrappers
                + self.ode_wrappers
                + self.python_function_wrappers
            ):
                uid = di.get_unique_id()
                md5.update(di.name, uid)
            self._unique_id_0 = md5.hexdigest()

        md5 = Hasher()
        md5.update("unique_id_0", self._unique_id_0)

        for di in self.fast_ode_wrappers + self.combined_ode_wrappers:
            uid = di.get_unique_id()
            md5.update(di.name, uid)

        md5.update("globals", self.globals_.get_unique_id())
        self._unique_id = md5.hexdigest()
        return self._unique_id

    @concat_generator_results
    def c_header(self):
        yield _gsl_related_header()
        yield _macros()
        yield _lsoda_header()
        yield _ode_fast_general_header()
        yield self.globals_.c_header()

        for wrapper in (
            self.function_wrappers
            + self.ode_wrappers
            + self.fast_ode_wrappers
            + self.combined_ode_wrappers
            + self.python_function_wrappers
            + list(self.visitor.extra_wrappers.values())
        ):
            yield wrapper.c_header()

    @concat_generator_results
    def c_code(self, header_file_path):
        yield """#include "{header_file_path}"\n""".format(
            header_file_path=header_file_path
        )
        yield self.globals_.c_code(header_file_path)

        one_ary_interface_class_code = create_interface_onary()

        yield one_ary_interface_class_code

        yield from _gsl_related_c_code()
        yield from _lsoda_related_c_code()
        yield from _lsoda_fast_related_c_code()

        for wrapper in (
            self.function_wrappers
            + self.ode_wrappers
            + self.fast_ode_wrappers
            + self.combined_ode_wrappers
            + self.python_function_wrappers
            + list(self.visitor.extra_wrappers.values())
        ):
            yield wrapper.c_code(header_file_path)

    @concat_generator_results
    def cython_code(self, header_file_path):
        yield from _general_cython_code(self._unique_id)
        yield from _gsl_related_cython_code(header_file_path)
        yield from _lsoda_fast_related_cython_code()

        yield self.globals_.cython_code(header_file_path)

        for wrapper in (
            self.function_wrappers
            + self.ode_wrappers
            + self.fast_ode_wrappers
            + self.combined_ode_wrappers
            + self.python_function_wrappers
            + list(self.visitor.extra_wrappers.values())
        ):
            yield wrapper.cython_code(header_file_path)

        yield from self.fast_ode_unique_id_function()

        yield self._pickling_code()

    def _pickling_code(self):
        names = []
        from .interpolation import InterpolationFunction1DWrapper

        for name, w in self.visitor.extra_wrappers.items():
            if isinstance(w, InterpolationFunction1DWrapper):
                names.append(str(name))

        return align(
            f"""
                |def __getstate__():
                |    data = [(name,
                |             eval("get_x_" + name + "()"),
                |             eval("get_y_" + name + "()"))
                |    for name in {names!r}]
                |    # print("get state", data)
                |    return data
                |
                |def __setstate__(data):
                |    # print("set state", data)
                |    for name, x, y in data:
                |         if x is not None:
                |             eval("set_" + name + "_values(x, y)")
                """
        )

    def fast_ode_unique_id_function(self):
        unique_ids = {
            wrapper.name: wrapper.ode.get_unique_id()
            for wrapper in self.fast_ode_wrappers
        }

        yield align(
            f"""
                |def get_fast_ode_unique_ids():
                |    return {unique_ids!r}
                """
        )
        yield align(
            """
            |def update_new_traces(unique_id, new_traces):
            |    from sympy2c.ode_fast import update_new_traces
            |    update_new_traces(unique_id, new_traces)
        """
        )

    def determine_required_extra_wrappers(self):
        pass

    def compile_and_load(
        self, root_folder=None, lsoda_folder=None, gsl_root=None, compilation_flags=None
    ):
        return compile_if_needed_and_load(
            self,
            root_folder,
            lsoda_folder,
            gsl_root,
            compilation_flags,
        )


def _macros():
    return align(
        """
    |inline double _min(double a, double b) {
    |       return (a < b) ? a : b;
    |}
    |
    |inline double _max(double a, double b) {
    |       return (a > b) ? a : b;
    |}
            """
    )


def _lsoda_header():
    return align(
        """
    |extern "C" {
    |    typedef void (*_lsoda_f) (double t, double *y, double *ydot, void *data);
    |    typedef void (*_lsoda_jac) (double t, double *y, double *jac, void *data);
    |
    |    void lsoda(_lsoda_f f, _lsoda_jac jac, int neq, double *y, double *t,
    |               double tout, int itol, double *rtol, double *atol, int itask,
    |               int *istate, int iopt, int jt, int iwork1, int iwork2, int iwork5,
    |               int iwork6, int iwork7, int iwork8, int iwork9, double rwork1,
    |               double rwork5, double rwork6, double rwork7, void *data);
    |
    |    void n_lsoda_terminate();
    |}
    """
    )


def _ode_fast_general_header():
    return align(
        """
    |#include <set>
    |#include <map>
    |#include <vector>
    |typedef std::set<std::vector<int>> TRACES;
    |typedef std::map<string, std::map<int, TRACES>> PT;
    |
    |PT get_new_traces();
    """
    )


def _general_cython_code(unique_id):
    from . import __version__

    yield align(
        """
           |# distutils: language = c++
           |
           |cimport libc.stdio as stdio
           |from libc.stdio cimport printf, fflush, stdout
           |from libc.stdlib cimport malloc
           |from posix.time cimport timeval, gettimeofday
           |from libcpp.vector cimport vector
           |from libcpp.set cimport set as cset
           |from libcpp.string cimport string
           |from libcpp.map cimport map
           |from libcpp.unordered_map cimport unordered_map
           |from cython.operator cimport dereference as deref, preincrement as inc
           |
           |cimport cython
           |
           |sympy2c_version = "{version}"
           |
           |cimport numpy as np
           |import numpy as np
           |import ctypes
           |
           |_api = {{}}
           |
           |cdef long microtime():
           |     cdef timeval time
           |     gettimeofday(&time, NULL)
           |     return (<unsigned long long>time.tv_sec * 1000000) + time.tv_usec
           |
           |import warnings
           |
           |def get_unique_id():
           |    return "{unique_id}"
           |
           """.format(unique_id=unique_id, version=__version__)
    )


def _gsl_related_header():
    return align(
        """
    |#include <cmath>
    |#include <cstdio>
    |#include <cstring>
    |#include <unordered_map>
    |#include <string>
    |
    |#include <gsl/gsl_integration.h>
    |#include <gsl/gsl_errno.h>
    |#include <gsl/gsl_spline.h>
    |#include <gsl/gsl_sf.h>
    |
    |
    |using namespace std;
    |
    |enum QuadPackMethod {
    |    QNG,
    |    QAG,
    |    QAGI
    |};
    |
    |extern "C" const char * get_last_error_message();
    |extern "C" const char * get_last_warning_message();
    |extern "C" void clear_last_error_message();
    |extern "C" void clear_last_warning_message();
    |extern "C" void set_eps_rel(string id, double value);
    |extern "C" void set_eps_abs(string id, double value);
    |extern "C" double get_rel_err(string id);
    |extern "C" double get_abs_err(string id);
    |extern "C" void set_eps_abs(string id, double value);
    |extern "C" void set_max_intervals(string id, size_t value);
    |extern "C" void set_quadpack_method(string id, QuadPackMethod m);
    |extern "C" void set_gsl_error_handler();
    |
    """
    )


def _gsl_related_c_code():
    yield align(
        """
        |#define BUFFER_SIZE_ERROR_MESSAGE 9999
        |
        |#define APPEND(buffer, buffer_size, what) do {\\
        |    strncat(buffer, what, buffer_size - strlen(buffer) - 1);\\
        |    } while(0)
        |
        |static char last_error_message[BUFFER_SIZE_ERROR_MESSAGE] = "";
        |static char last_warning_message[BUFFER_SIZE_ERROR_MESSAGE] = "";
        |
        |void set_error_message_gsl(const char * prefix, int code)
        |{
        |    clear_last_error_message();
        |    APPEND(last_error_message, BUFFER_SIZE_ERROR_MESSAGE, prefix);
        |    APPEND(last_error_message, BUFFER_SIZE_ERROR_MESSAGE, ": ");
        |    APPEND(last_error_message, BUFFER_SIZE_ERROR_MESSAGE, gsl_strerror(code));
        |}
        |
        |double set_error_message(const char * message)
        |{
        |    clear_last_error_message();
        |    APPEND(last_error_message, BUFFER_SIZE_ERROR_MESSAGE, message);
        |    return NAN;
        |}
        |
        |void set_warning_message(const char * message)
        |{
        |    clear_last_error_message();
        |    APPEND(last_warning_message, BUFFER_SIZE_ERROR_MESSAGE, message);
        |}
        |
        |static unordered_map<string, double> id_to_eps_rel = {{"default", 1e-6}};
        |static unordered_map<string, double> id_to_eps_abs = {{"default", 0.0 }};
        |static unordered_map<string, size_t> id_to_max_intervals = {{"default", 1000}};
        |static unordered_map<string, QuadPackMethod> id_to_quadpack_method
        |                                             = {{"default", QAG}};
        |
        |static unordered_map<string, double> id_to_rel_err = {{ }};
        |static unordered_map<string, double> id_to_abs_err = {{ }};

        |extern "C" {
        |    const char * get_last_error_message() { return last_error_message; }
        |    const char * get_last_warning_message() { return last_warning_message; }
        |    void clear_last_error_message() { last_error_message[0] = 0; }
        |    void clear_last_warning_message() { last_warning_message[0] = 0; }
        |
        |    void set_eps_rel(string id, double value) { id_to_eps_rel[id] = value; }
        |    void set_eps_abs(string id, double value) { id_to_eps_abs[id] = value; }
        |
        |    void set_rel_err(string id, double value) { id_to_rel_err[id] = value; }
        |    void set_abs_err(string id, double value) { id_to_abs_err[id] = value; }
        |
        |    double get_rel_err(string id) {
        |        return id_to_rel_err.count(id) > 0 ? id_to_rel_err[id]: -1.0;
        |    }
        |    double get_abs_err(string id) {
        |        return id_to_abs_err.count(id) > 0 ? id_to_abs_err[id]: -1.0;
        |    }
        |
        |    void set_max_intervals(string id, size_t value) {
        |        id_to_max_intervals[id] = value;
        |    }
        |    void set_quadpack_method(string id, QuadPackMethod m) {
        |         id_to_quadpack_method[id] = m;
        |    }
        |}
        |
        |void handler (const char * reason, const char * file, int line, int gsl_errno)
        |{
        |
        |    last_error_message[0] = 0;
        |    char buffer[200];
        |    snprintf(buffer, 200, " (line %d): %s, ", line, reason);
        |    APPEND(last_error_message, BUFFER_SIZE_ERROR_MESSAGE, file);
        |    APPEND(last_error_message, BUFFER_SIZE_ERROR_MESSAGE, buffer);
        |    APPEND(last_error_message, BUFFER_SIZE_ERROR_MESSAGE,
        |           gsl_strerror(gsl_errno));
        |
        |}
        |
        |void set_gsl_error_handler() {
        |   gsl_set_error_handler(handler);
        |}
        |
        |inline double gsl_function_eval(double x, void * curried_function)
        |{
        |   OneAryFunction * func = (OneAryFunction *) curried_function;
        |   return (*func)(x);
        |}
        |
        |#define BUFFER_SIZE_SMALL 100
        |
        |#define REPORT_ERROR(fmt, arg, code) do { \\
        |    snprintf(buffer, BUFFER_SIZE_SMALL, fmt, arg); \\
        |    set_error_message_gsl(buffer, code); \\
        |   } while(0)
        |
        |#define REPORT_WARNING(fmt, arg) do { \\
        |    snprintf(buffer, BUFFER_SIZE_SMALL, fmt, arg); \\
        |    set_warning_message(buffer); \\
        |   } while(0)
        |
        |double quadpack_integration(OneAryFunction *f, const char *id,
        |                            double low, double high) {
        |    double result, error, eps_rel, eps_abs;
        |    size_t max_intervals;
        |    QuadPackMethod method;
        |    int err_code;
        |    unordered_map<string, double>::const_iterator found_eps;
        |    unordered_map<string, size_t>::const_iterator found_max_intervals;
        |    unordered_map<string, QuadPackMethod>::const_iterator found_method;
        |    char buffer[BUFFER_SIZE_SMALL];
        |
        |    found_method = id_to_quadpack_method.find(id);
        |    if (found_method != id_to_quadpack_method.end())
        |         method = found_method->second;
        |    else {
        |         REPORT_ERROR("no quadpack method set for id '%s'", id, GSL_EINVAL);
        |         return GSL_EINVAL;
        |    }
        |
        |    if (std::isinf(low) || std::isinf(high)) {
        |        if (method != QAGI) {
        |            //REPORT_WARNING(
        |            //    "switched to QAGI for infinite limit(s) for id '%s'", id
        |            //);
        |            method = QAGI;
        |        }
        |    }
        |    else if (method == QAGI) {
        |       REPORT_ERROR("you must not use QAGI for finite limit(s) for id '%s'",
        |                     id, GSL_EINVAL);
        |       return GSL_EINVAL;
        |
        |    }
        |
        |    found_eps = id_to_eps_rel.find(id);
        |    if (found_eps != id_to_eps_rel.end())
        |         eps_rel = found_eps->second;
        |    else {
        |         REPORT_ERROR("no eps_rel value set for id '%s'", id, GSL_EINVAL);
        |         return GSL_EINVAL;
        |    }
        |
        |    found_eps = id_to_eps_abs.find(id);
        |    if (found_eps != id_to_eps_abs.end())
        |          eps_abs = found_eps->second;
        |    else {
        |         REPORT_ERROR("no eps_abs value set for id '%s'", id, GSL_EINVAL);
        |         return GSL_EINVAL;
        |    }
        |
        |    gsl_function F;
        |    F.function = gsl_function_eval;
        |    F.params = (void *)f;
        |
        |    gsl_integration_workspace *w;
        |    /* gsl_set_error_handler_off(); */
        |    clear_last_error_message();
        |
        |    if (method == QAG) {
        |        found_max_intervals = id_to_max_intervals.find(id);
        |        if (found_max_intervals != id_to_max_intervals.end())
        |             max_intervals = found_max_intervals->second;
        |        else {
        |            REPORT_ERROR(
        |                "no max_intervals value set for id '%s'", id, GSL_EINVAL
        |            );
        |            return GSL_EINVAL;
        |        }
        |
        |        w = gsl_integration_workspace_alloc(max_intervals);
        |
        |        err_code = gsl_integration_qag(&F, low, high, eps_abs, eps_rel,
        |                                       max_intervals, GSL_INTEG_GAUSS31, w,
        |                                       &result, &error);
        |
        |        if (err_code) {
        |            set_error_message_gsl("qag from gsl returned", err_code);
        |            set_abs_err(id, -1.0);
        |            set_rel_err(id, -1.0);
        |            }
        |        else {
        |            set_abs_err(id, error);
        |            set_rel_err(id, error / result);
        |        }
        |        gsl_integration_workspace_free(w);
        |
        |    } else if (method == QAGI) {
        |
        |        double sign = 1.0;
        |        double temp;
        |        if (low > high) {
        |            sign = -1.0;
        |            temp = low;
        |            low = high;
        |            high= temp;
        |        }
        |
        |        found_max_intervals = id_to_max_intervals.find(id);
        |        if (found_max_intervals != id_to_max_intervals.end())
        |             max_intervals = found_max_intervals->second;
        |        else {
        |            REPORT_ERROR(
        |                "no max_intervals value set for id '%s'", id, GSL_EINVAL
        |            );
        |            return GSL_EINVAL;
        |        }
        |
        |        w = gsl_integration_workspace_alloc(max_intervals);
        |
        |        if (std::isinf(low) && std::isinf(high)) {
        |            err_code = gsl_integration_qagi(&F, eps_abs, eps_rel,
        |                                            max_intervals,w, &result, &error);
        |            if (err_code)
        |                set_error_message_gsl("qagi from gsl returned", err_code);
        |        }
        |        else if (std::isinf(low)) {
        |            err_code = gsl_integration_qagil(&F, high, eps_abs, eps_rel,
        |                                           max_intervals, w, &result, &error);
        |            if (err_code)
        |                set_error_message_gsl("qagil from gsl returned", err_code);
        |        }
        |        else {
        |            err_code = gsl_integration_qagiu(&F, low, eps_abs, eps_rel,
        |                                           max_intervals, w, &result, &error);
        |            if (err_code)
        |                set_error_message_gsl("qagiu from gsl returned", err_code);
        |        }
        |        result *= sign;
        |
        |        if (err_code) {
        |            set_error_message_gsl("qagi from gsl returned", err_code);
        |            set_abs_err(id, -1.0);
        |            set_rel_err(id, -1.0);
        |            }
        |        else {
        |            set_abs_err(id, error);
        |            set_rel_err(id, error / result);
        |        }
        |
        |        gsl_integration_workspace_free(w);
        |
        |    } else {
        |
        |        size_t neval;
        |        err_code = gsl_integration_qng(&F, low, high, eps_abs, eps_rel,
        |                                       &result, &error, &neval);
        |
        |        if (err_code) {
        |            set_error_message_gsl("qagi from gsl returned", err_code);
        |            set_abs_err(id, -1.0);
        |            set_rel_err(id, -1.0);
        |            }
        |        else {
        |            set_abs_err(id, error);
        |            set_rel_err(id, error / result);
        |        }
        |    }
        |
        |    return result;
        |}
        |
        |typedef struct
        |   {
        |   double * c;
        |   double * g;
        |   double * diag;
        |   double * offdiag;
        |} cspline_state_t;
        |
        |static inline void
        |coeff_calc (const double c_array[], double dy, double dx, size_t index,
        |            double * b, double * c, double * d)
        |{
        |    const double c_i = c_array[index];
        |    const double c_ip1 = c_array[index + 1];
        |    *b = (dy / dx) - dx * (c_ip1 + 2.0 * c_i) / 3.0;
        |    *c = c_i;
        |    *d = (c_ip1 - c_i) / (3.0 * dx);
        |}
        |
        |static
        |void
        |cspline_eval_vector_sorted (const void * vstate,
        |            const double x_array[], const double y_array[], size_t size,
        |            double *x, int n,
        |            double *y)
        |{
        |    const cspline_state_t *state = (const cspline_state_t *) vstate;
        |
        |    double x_lo, x_hi;
        |    double dx;
        |    double xi;
        |    size_t index = 0;
        |
        |    index = gsl_interp_bsearch (x_array, x[0], 0, size - 1);
        |
        |    for (size_t ii=0; ii < n; ++ii) {
        |        xi = x[ii];
        |        y[ii] = NAN;
        |
        |        if (xi < x_array[0]) continue;
        |        if (xi > x_array[size - 1]) continue;
        |        while ((xi < x_array[index] || xi >= x_array[index + 1])
        |               && index < size - 2)
        |                   index ++;
        |       if (index < size - 2)
        |           if (xi < x_array[index] || xi >= x_array[index + 1]) {
        |              // printf("no match %d %lf %lf %lf\\n", index, xi, x_array[index], x_array[index + 1]);
        |              continue;
        |        }
        |
        |        if (index == size - 2)
        |           if (xi < x_array[index] || xi > x_array[index + 1]) {
        |              // printf("no match %d %lf %lf %lf\\n", index, xi, x_array[index], x_array[index + 1]);
        |              continue;
        |        }
        |
        |        /* evaluate */
        |        x_hi = x_array[index + 1];
        |        x_lo = x_array[index];
        |        dx = x_hi - x_lo;
        |        if (dx > 0.0) {
        |            const double y_lo = y_array[index];
        |            const double y_hi = y_array[index + 1];
        |            const double dy = y_hi - y_lo;
        |            double delx = xi - x_lo;
        |            double b_i, c_i, d_i;
        |            coeff_calc(state->c, dy, dx, index,  &b_i, &c_i, &d_i);
        |            // printf("%d %lf %lf %lf %lf %lf\\n", index, dy, dx, b_i, c_i, d_i);
        |            y[ii] = y_lo + delx * (b_i + delx * (c_i + delx * d_i));
        |        }
        |    }
        |}
        """
    )


def _gsl_related_cython_code(header_file_path):
    yield align(
        """
           |cdef extern from "{header_file_path}":
           |
           |    enum QuadPackMethod:
           |        QNG
           |        QAG
           |        QAGI
           |
           |cdef extern from "{header_file_path}":
           |
           |    char * c_get_last_error_message "get_last_error_message"()
           |    char * c_get_last_warning_message "get_last_warning_message"()
           |    void clear_last_error_message()
           |    void clear_last_warning_message()
           |    void set_gsl_error_handler()
           |    void c_set_eps_rel "set_eps_rel"(string, double)
           |    void c_set_eps_abs "set_eps_abs"(string, double)
           |
           |    void c_set_rel_err "set_rel_err"(string, double)
           |    void c_set_abs_err "set_abs_err"(string, double)
           |    double c_get_rel_err "get_rel_err"(string)
           |    double c_get_abs_err "get_abs_err"(string)
           |
           |    void c_set_max_intervals "set_max_intervals"(string, size_t)
           |    void c_set_quadpack_method "set_quadpack_method"(string, QuadPackMethod)
           |
           |def get_last_error_message():
           |    return str(c_get_last_error_message(), "utf-8")
           |
           |def get_last_warning_message():
           |    return str(c_get_last_warning_message(), "utf-8")
           |
        """.format(header_file_path=header_file_path)
    )

    yield align(
        """
        |def set_eps_rel(str id, double value):
        |    c_set_eps_rel(id.encode("ascii"), value)
        |
        |def set_eps_abs(str id, double value):
        |    c_set_eps_abs(id.encode("ascii"), value)
        |
        |def set_max_intervals(str id, size_t value):
        |    c_set_max_intervals(id.encode("ascii"), value)
        |
        |def set_quadpack_method(str id, str value):
        |    if value == "QNG":
        |       c_set_quadpack_method(id.encode("ascii"), QuadPackMethod.QNG)
        |    elif value == "QAG":
        |       c_set_quadpack_method(id.encode("ascii"), QuadPackMethod.QAG)
        |    elif value == "QAGI":
        |       c_set_quadpack_method(id.encode("ascii"), QuadPackMethod.QAGI)
        |    else:
        |       raise ValueError("unknown quadpack method {}".format(value))
        |
        |set_gsl_error_handler()
        |
        |def get_abs_err(str id):
        |    return c_get_abs_err(id.encode("ascii"))
        |def get_rel_err(str id):
        |    return c_get_rel_err(id.encode("ascii"))
        """
    )


def _lsoda_fast_related_c_code():
    yield align(
        r"""
            |double SEC_FACTOR=1;
            |extern "C" void _set_sec_factor(double sf) { SEC_FACTOR = sf; }
            |
            |PT _new_traces;
            |PT get_new_traces() { return _new_traces; }
            |
            |#include <chrono>
            |typedef std::chrono::high_resolution_clock clock_;
            |static std::chrono::time_point<clock_> m_beg;
            |
            |void reset_timer() { m_beg = clock_::now(); }
            |
            |float time_delta() {
            |    return 1e-9 * std::chrono::duration_cast<std::chrono::nanoseconds>(
            |                clock_::now() - m_beg).count();
            |}
            """
    )


def _lsoda_related_c_code():
    yield align(
        r"""
        |
        |#include<cstdio>
        |#include<cmath>
        |#include<list>
        |#include<vector>
        |#include<array>
        |
        |#define doublereal double
        |#define integer long int
        |
        |extern "C" struct {
        |    doublereal rowns[209], ccmax, el0, h, hmin, hmxi, hu, rc, tn, uround;
        |    integer illin, init, lyh, lewt, lacor, lsavf, lwm, liwm, mxstep, mxhnil,
        |    nhnil, ntrep, nslast, nyh, iowns[6], icf, ierpj, iersl, jcur,
        |    jstart, kflag, l, meth, miter, maxord, maxcor, msbp, mxncf, n, nq,
        |    nst, nfe, nje, nqu;
        |} ls0001_;
        |struct _solver_change {
        |    _solver_change(double _t,
        |                  int _from,
        |                  int _to): t(_t), from(_from), to(_to) {};
        |    double t;
        |    int from, to;
        |};

    """
    )


def _lsoda_fast_related_cython_code():
    yield align(
        """
        |ctypedef int (*S_fp)(...)
        |ctypedef int (*U_fp)(...)
        |ctypedef void (*V_fp)(...)
        |ctypedef double (*D_fp)(...)
        |
        |cdef extern:
        |    int lsodafast_(S_fp f, U_fp econ, long int *neq, double *y,
        |        double *t, double *tout, long int *itol, double *rtol,
        |        double *atol, long int *itask, long int *istate, long int *iopt,
        |        double *rwork, long int *lrw, long int *iwork, long int *liw,
        |        U_fp jac, long int *jt, V_fp lu_solver, D_fp fnorm_computation,
        |        V_fp step_size_callback, long *handle) nogil
        |
        |    cdef struct ls0001_struct:
        |        double rowns[209], ccmax, el0, h, hmin, hmxi, hu, rc, tn, uround
        |        long illin, init, lyh, lewt, lacor, lsavf, lwm, liwm, mxstep, mxhnil
        |        long nhnil, ntrep, nslast, nyh, iowns[6], icf, ierpj, iersl, jcur
        |        long jstart, kflag, l, meth, miter, maxord, maxcor, msbp, mxncf, n, nq
        |        long nst, nfe, nje, nqu
        |
        |    ls0001_struct ls0001_
        |
        |    void _set_sec_factor(double)
        |
        |cdef extern from "functions.hpp":
        |  map[string, map[int, cset[vector[int]]]] c_get_new_traces "get_new_traces" ()
        |
        |cpdef get_new_traces(str id_):
        |   cdef string id__ = id_.encode("utf-8")
        |
        |   cdef dict result = {}
        |
        |   cdef map[int, cset[vector[int]]] traces = c_get_new_traces()[id__];
        |   cdef map[int, cset[vector[int]]].iterator it_levels
        |   cdef cset[vector[int]].iterator it_level_traces
        |
        |   result = {}
        |
        |   it_levels = traces.begin()
        |
        |   while it_levels != traces.end():
        |       level = deref(it_levels).first
        |       level_traces = deref(it_levels).second
        |       it_level_traces = level_traces.begin()
        |       result[level] = []
        |       while it_level_traces != level_traces.end():
        |           trace = deref(it_level_traces)
        |           py_trace = [trace[k] for k in range(trace.size())]
        |           result[level].append(py_trace)
        |           inc(it_level_traces)
        |       inc(it_levels)
        |   return result
        |
        |
        |def set_sec_factor(double factor):
        |    _set_sec_factor(factor)
        |
        |ctypedef vector[double]* vec_double_ptr
        |cdef unordered_map[long, vec_double_ptr] _hvalues = unordered_map[long, vec_double_ptr ]()
        |
        |cdef void _hvalue_callback(long *handle, double *h) nogil:
        |    cdef vector[double]* hvalues_c = _hvalues.at(deref(handle))
        |    deref(hvalues_c).push_back(deref(h))
        """
    )
