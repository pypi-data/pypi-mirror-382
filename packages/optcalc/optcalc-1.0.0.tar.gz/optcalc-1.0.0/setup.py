import os
from setuptools import setup, Extension
import sysconfig
import numpy

this_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(this_dir, 'optcalc')

# printa sökvägen för säkerhets skull
print(f"Header directory: {src_dir}")

module = Extension(
    'optcalc.optcalc',
    sources=[
        os.path.join(src_dir, 'optcalc.c'),
        os.path.join(src_dir, 'calc.c')
    ],
    include_dirs=[
        sysconfig.get_paths()['include'],
        numpy.get_include(),
        src_dir,
        os.path.abspath(src_dir)  # <-- lägg till absolut path också
    ],
    extra_compile_args=['-O2']
)

setup(
    name='optcalc',
    version='1.0.0',
    description='Black-Scholes option calculator written in C (fast Python extension)',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='Björn Hallström',
    license='MIT',
    url='https://github.com/bjorn7474',  # valfritt men rekommenderas
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    packages=['optcalc'],
    ext_modules=[module],
    python_requires='>=3.8',
)

