#!/usr/bin/env python

import glob
import os
import shutil
import subprocess

from setuptools._distutils import ccompiler

from .utils import create_folder_if_not_exists, get_platform

HERE = os.path.dirname(os.path.abspath(__file__))


def install_f2c_if_needed(cache_folder):
    folder = os.path.join(cache_folder, "sympy2c", get_platform(), "libf2c")
    lib_name = "libf2c.a"
    lib_path = os.path.join(folder, lib_name)
    if os.path.exists(lib_path):
        return lib_path

    create_folder_if_not_exists(folder)
    for path in glob.glob(os.path.join(HERE, "f2c_files", "*")):
        shutil.copy(path, folder)

    current_folder = os.getcwd()
    CC = os.environ.get("CC", ccompiler.new_compiler().executables["compiler"][0])

    try:
        os.chdir(folder)
        output = subprocess.check_output(
            [
                CC,
                "-O3",
                "-fPIC",
                "-c",
                "-DINTEGER_STAR_8=1",
                # "-w",
                "-Wfatal-errors",
                *glob.glob("*.c"),
            ],
            shell=False,
            universal_newlines=True,
        )
        print(output)

        output = subprocess.check_output(
            [
                "ar",
                "rcs",
                lib_name,
                *glob.glob("*.o"),
            ],
            shell=False,
            universal_newlines=True,
        )
        print(output)
    finally:
        os.chdir(current_folder)
    return lib_path
