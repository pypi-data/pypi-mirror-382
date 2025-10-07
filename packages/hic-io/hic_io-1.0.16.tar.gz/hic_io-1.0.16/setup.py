from glob import glob
from pybind11 import get_include
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup


ext_modules = [
    Pybind11Extension(
        "hic_io",
        sources=[
            "hic_io/python_binding.cpp",
        ],
        include_dirs=[
            "hic_io/",
            get_include(),
        ],
        libraries=["curl", "z"],
        language="c++",
        cxx_std=17,
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    data_files=[(
        "hic_io",
            glob("hic_io/**/*.c", recursive=True) +
            glob("hic_io/**/*.h", recursive=True) +
            glob("hic_io/**/*.cpp", recursive=True) +
            glob("hic_io/**/*.hpp", recursive=True)
        )
    ],
)
