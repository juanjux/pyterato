# -*- coding: utf-8 -*-

from pyd.support import setup, Extension
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

description = long_descr = "Python application to lint Spanish literary language from LibreOffice"

main_ns = {}
with open("pyterato/version.py") as ver_file:
    exec(ver_file.read(), main_ns)

version = main_ns['__version__']
setup(
    name = "pyterato",
    version = version,

    description = description,
    long_description = long_descr,
    license = "GPL 3",
    url = "https://github.com/juanjux/pyterato",
    download_url = "https://github.com/juanjux/pyterato/archive/%s.tar.gz" % version,
    author = "Juanjo Alvarez Martinez",
    author_email = "juanjo@juanjoalvarez.net",
    packages = find_packages(exclude=["tests"]),
    entry_points = {
        "console_scripts": [
            "pyterato = pyterato.cli:main"
        ]
    },
    install_requires = [],
    extras_require = {},
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Other Audience",
        "Topic :: Office/Business",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6"
    ],
    ext_modules=[
        Extension('pyterato_native', ['native/checks.d', 'native/pyterato_native.d', 'native/checks_data.d'],
            extra_compile_args=['-release', '-boundscheck=off', '-inline'],
            # extra_compile_args=['-w', '-g', '-debug'],
            build_deimos=True,
            optimize=True,
            d_lump=True),
    ],
)
