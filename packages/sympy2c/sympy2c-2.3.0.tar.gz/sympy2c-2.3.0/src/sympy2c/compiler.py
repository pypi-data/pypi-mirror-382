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

import ctypes
import glob
import hashlib
import importlib
import os
import subprocess
import sys
import threading
import time
import warnings
from contextlib import contextmanager
from functools import lru_cache, partial

from .utils import (
    align,
    base_cache_folder,
    create_folder_if_not_exists,
    get_platform,
    sympy2c_cache_folder,
)

HERE = os.path.dirname(os.path.abspath(__file__))


ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]

ctypes.pythonapi.PyCapsule_GetName.restype = ctypes.c_char_p
ctypes.pythonapi.PyCapsule_GetName.argtypes = [ctypes.py_object]


def compile_if_needed_and_load(
    module_wrapper,
    root_folder,
    lsoda_root_folder,
    gsl_root,
    compilation_flags,
    cache_folder=None,
):
    from .build_f2c import install_f2c_if_needed
    from .build_gsl import install_gsl_if_needed
    from .build_lsoda import install_lsoda_if_needed
    from .build_lsoda_fast import install_lsoda_fast_if_needed

    if cache_folder is None:
        cache_folder = base_cache_folder()

    if gsl_root is None:
        gsl_root = os.path.join(cache_folder, "sympy2c", get_platform(), "gsl")

    if not os.path.exists(gsl_root) or (
        not os.path.exists(os.path.join(gsl_root, "include"))
        or not os.path.exists(os.path.join(gsl_root, "lib"))
    ):
        install_gsl_if_needed(gsl_root)

    bf = build_folder(module_wrapper, compilation_flags, root_folder)

    libf2c_path = install_f2c_if_needed(cache_folder)
    lsoda_object_file = install_lsoda_if_needed(lsoda_root_folder)
    lsoda_fast_static_lib = install_lsoda_fast_if_needed(lsoda_root_folder)

    generate_files_and_compile_if_needed(
        wrapper_id(module_wrapper, compilation_flags),
        bf,
        module_wrapper,
        gsl_root,
        lsoda_object_file,
        lsoda_fast_static_lib,
        libf2c_path,
        compilation_flags,
    )
    module = LoadedModule(bf)
    return module


def generate_files_and_compile_if_needed(
    wrapper_id,
    build_folder,
    module_wrapper,
    gsl_root,
    lsoda_object_file,
    lsoda_fast_static_lib,
    libf2c_path,
    compilation_flags,
):
    from .integral import IntegralFunctionWrapper

    IntegralFunctionWrapper.reset()

    if glob.glob(
        os.path.join(build_folder, "_wrapper_{}.so".format(wrapper_id), "setup.py")
    ):
        print("wrapper already exists at", build_folder)
        return build_folder

    create_folder_if_not_exists(build_folder)

    build = os.environ.get("REBUILD_WRAPPER") or not glob.glob(
        os.path.join(build_folder, "_wrapper_{}.pyx".format(wrapper_id))
    )
    if build:
        print("create source files at", build_folder)
        create_source_files(
            build_folder,
            module_wrapper,
            gsl_root,
            lsoda_object_file,
            lsoda_fast_static_lib,
            libf2c_path,
            wrapper_id,
            compilation_flags,
        )
    else:
        print("source files already exist at", build_folder)
    compile_files(build_folder)


@lru_cache()
def warn_new_traces(unique_id):
    from .ode_fast import read_new_traces

    if read_new_traces(unique_id):
        warnings.warn("there are new permuations pending, you might want to recompile")


class LoadedModule:
    """wraps compiled module to support pickling"""

    def __init__(self, folder):
        self._folder = os.path.abspath(folder)
        self._wrapper_id = os.path.basename(folder)
        self._module_name = "_wrapper_" + self._wrapper_id
        self._load()

    def _load(self, state=None):
        if self._module_name in sys.modules:
            del sys.modules[self._module_name]
        try:
            before = os.getcwd()
            os.chdir(self._folder)
            sys.path.insert(0, self._folder)
            self._module = importlib.import_module(self._module_name)
            if state is not None:
                self._module.__setstate__(state)
        except FileNotFoundError:
            raise ImportError()
        finally:
            sys.path.pop(0)
            os.chdir(before)
        for unique_id in self._module.get_fast_ode_unique_ids().values():
            warn_new_traces(unique_id)

    def reload(self):
        self._load()

    def __getattr__(self, name):
        if name.startswith("solve_fast"):
            solver = getattr(self._module, name)
            return partial(solver, self)
        if name in self._module._api:
            _fun = setup_function(name, self._module)
            setattr(self._module, name, _fun)
            return _fun

        return getattr(self._module, name)

    def __getstate__(self):
        return self._folder, self._module_name, self._module.__getstate__()

    def __setstate__(self, data):
        try:
            self._folder, self._module_name, state = data
            self._load(state)
        except Exception:
            import traceback

            traceback.print_exc()

    def __dir__(self):
        return self._module.__dir__()


@lru_cache
def setup_function(name, module):
    import numba  # noqa: F401
    import numpy as np  # noqa: F401
    from numba import float64, njit  # noqa: F401

    res_spec, arg_types, args, vector_flags, numba_signature = module._api[name]

    capsule = module.__pyx_capi__[f"_api_{name}"]

    fun_ptr = ctypes.pythonapi.PyCapsule_GetPointer(
        capsule, ctypes.pythonapi.PyCapsule_GetName(capsule)
    )
    res_type, res_shape = res_spec
    fun = ctypes.CFUNCTYPE(
        ctypes.c_int,
        *(arg_types + [res_type]),
    )(fun_ptr)

    ctype_args = ", ".join(
        [
            f"{arg}" + (".ctypes" if is_vector else "")
            for (is_vector, arg) in zip(vector_flags, args)
        ]
        + ["__result.ctypes"]
    )
    arg_decl = ", ".join(args)
    numba_decorator = (
        f"@numba.jit([{numba_signature}], nopython=True)"
        if not vector_flags or any(vector_flags)
        else f"@numba.vectorize([{numba_signature}], nopython=True)"
    )
    code = align(
        f"""
    |import numpy as np
    |{numba_decorator}
    |def {name}({arg_decl}):
    |    __result = np.zeros({res_shape if res_shape is not None else (1,)})
    |
    |    retcode = fun({ctype_args})
    |    if retcode == 1:
    |        raise ArithmeticError("calling {name} did not succeed, "
    |                 "use get_last_error() function for details.")
    |    if retcode == 2:
    |        print("calling {name} issued a warning, "
    |              "use get_last_warning() function for details.")
    |    return {"__result[0]" if res_shape is None else "__result"}
    """
    )
    lo = dict(locals())
    gl = dict(globals())
    gl["fun"] = fun
    gl["np"] = np
    exec(code, gl, lo)
    return lo[name]


# for backwards compatibility:
load_module = LoadedModule


def create_source_files(
    build_folder,
    module_wrapper,
    gsl_root,
    lsoda_object_file,
    lsoda_fast_static_lib,
    libf2c_path,
    wrapper_id,
    compilation_flags,
):
    j = partial(os.path.join, build_folder)

    print("setup code generation")
    module_wrapper.setup_code_generation()

    with open(j("functions.cpp"), "w") as fh:
        print(module_wrapper.c_code("functions.hpp"), file=fh)

    with open(j("functions.hpp"), "w") as fh:
        print(module_wrapper.c_header(), file=fh)

    with open(
        j("_wrapper_{wrapper_id}.pyx".format(wrapper_id=wrapper_id)),
        "w",
    ) as fh:
        print(module_wrapper.cython_code("functions.hpp"), file=fh)

    if not compilation_flags:
        compilation_flags = ["-O3"]

    setup_py_content = align(
        """
    |from distutils.core import setup
    |from distutils.extension import Extension
    |from distutils.sysconfig import get_config_vars
    |
    |from Cython.Build import cythonize
    |import numpy as np
    |import glob
    |import os
    |import sys
    |
    |get_config_vars()["CC"] = os.environ.get("CC", get_config_vars()["CC"])
    |get_config_vars()["CXX"] = os.environ.get("CXX", get_config_vars()["CXX"])
    |
    |sourcefiles = ['_wrapper_{wrapper_id}.pyx', 'functions.cpp']
    |
    |if (os.environ.get("CC") == "clang" or get_config_vars()['CC'] == 'clang'
    |    or sys.platform == "darwin"):
    |        libf2c = ['{libf2c}']
    |        link_flags = []
    |else:
    |        libf2c = ['-Wl,--whole-archive', '{libf2c}', '-Wl,--no-whole-archive']
    |        link_flags = ["-Wl,--allow-multiple-definition"]
    |
    |extensions = [Extension("_wrapper_{wrapper_id}",
    |                sourcefiles,
    |                define_macros = [('HAVE_INLINE', '1'),
    |                                 ('CYTHON_EXTERN_C', 'extern "C"')],
    |                include_dirs=['{gsl_root}/include', np.get_include(),],
    |                library_dirs=['{gsl_root}/lib'],
    |                extra_compile_args = {compilation_flags} +
    |                          ["-std=c++11",
    |                           "-fPIC",
    |                           "-DINTEGER_STAR_8=1",
    |                           "-pipe",
    |                           "-Wno-unused-variable",
    |                           "-fno-var-tracking",
    |                           "-Wno-unused-but-set-variable",
    |                           ],
    |                extra_link_args = ["-fPIC",
    |                                   "-u s_stop",
    |                                   ] + link_flags,
    |                extra_objects = (['{gsl_root}/lib/libgsl.a', '{lsoda_object_file}',
    |                                  '{lsoda_fast_static_lib}']
    |                                 + libf2c
    |                                 )
    |                )
    |              ]
    |
    |setup(
    |   ext_modules=cythonize(extensions, language="c++")
    |)
    """
    ).format(
        gsl_root=gsl_root,
        lsoda_object_file=lsoda_object_file,
        lsoda_fast_static_lib=lsoda_fast_static_lib,
        libf2c=libf2c_path,
        wrapper_id=wrapper_id,
        compilation_flags=compilation_flags,
    )

    with open(j("setup.py"), "w") as fh:
        print(setup_py_content, file=fh)


def compile_files(folder):
    if not os.environ.get("REBUILD_WRAPPER"):
        try:
            LoadedModule(folder)
            return
        except ImportError:
            pass
    current_folder = os.getcwd()
    try:
        os.chdir(folder)
        print()
        print("compile python extension module")
        s = time.time()
        run_command("python setup.py build_ext --inplace")
        print(
            "compiling the module needed {:.1f} minutes".format((time.time() - s) / 60)
        )
    finally:
        os.chdir(current_folder)


def run_command(cmd):
    print("$", cmd)
    with monitor():
        proc = subprocess.run(
            cmd,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
        )
    if proc.returncode:
        print(proc.stdout)
        raise OSError("compilation failed")


@contextmanager
def monitor():
    t = PrintAliveThread()
    t.start()
    try:
        yield
    finally:
        t.running = False
        time.sleep(0.05)
        print()
        t.join()


class PrintAliveThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        started = time.time()
        while self.running:
            while time.time() < started + 1.0:
                if not self.running:
                    return
                time.sleep(0.05)
            started = time.time()
            print(".", end="")
            sys.stdout.flush()


def build_folder(module_wrapper, compilation_flags, root_folder=None):
    if root_folder is None:
        root_folder = sympy2c_cache_folder()
    return os.path.join(
        root_folder,
        wrapper_id(
            module_wrapper,
            compilation_flags,
        ),
    )


def wrapper_id(module_wrapper, *extra):
    extra_str = ("".join(str(e) for e in extra)).encode("ascii")
    return "{}_{}".format(
        module_wrapper.get_unique_id(), hashlib.md5(extra_str).hexdigest()[:5]
    )
