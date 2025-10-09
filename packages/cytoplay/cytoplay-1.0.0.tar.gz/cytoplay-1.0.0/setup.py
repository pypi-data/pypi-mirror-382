"""Cytosim: Langevin dynamics of active polymer networks

Cytosim is a simulation tool for cytoskeleton and polymers.
"""
# setup.py inspired by mem3dg's : https://github.com/RangamaniLabUCSD/Mem3DG
# and from deepmind's tree's :    https://github.com/deepmind/tree/
import os
import sys
import subprocess
import re
import platform
import shutil
import sysconfig
import setuptools
import pathlib
from setuptools.command import build_ext
from setuptools import setup
from setuptools import find_packages

version = "1.0.0"
cmake_args=[]


if('CONDA_PREFIX' in os.environ):
    print("Setting library search path (CMAKE_PREFIX_PATH): %s"%(os.environ['CONDA_PREFIX']))
    cmake_args.append('-DCMAKE_PREFIX_PATH=%s'%(os.environ['CONDA_PREFIX']))

DOCLINES = __doc__.split("\n")

CLASSIFIERS = """\
Development Status :: 3 - Alpha
Environment :: Console
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: C++
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: Implementation :: CPython
Topic :: Scientific/Engineering :: Chemistry
Topic :: Scientific/Engineering :: Mathematics
Topic :: Scientific/Engineering :: Physics
Topic :: Scientific/Engineering :: Visualization
"""

class CMakeExtension(setuptools.Extension):
  """An extension with no sources.

  We do not want distutils to handle any of the compilation (instead we rely
  on CMake), so we always pass an empty list to the constructor.
  """

  def __init__(self, name, source_dir=''):
    super().__init__(name, sources=[])
    self.source_dir = os.path.abspath(source_dir)


class BuildCMakeExtension(build_ext.build_ext):
  """Our custom build_ext command.

  Uses CMake to build extensions instead of a bare compiler (e.g. gcc, clang).
  """

  def run(self):
    self._check_build_environment()
    for ext in self.extensions:
      self.build_extension(ext)

  def _check_build_environment(self):
    """Check for required build tools: CMake, C++ compiler, and python dev."""
    try:
      subprocess.check_call(['cmake', '--version'])
    except OSError as e:
      ext_names = ', '.join(e.name for e in self.extensions)
      raise RuntimeError(
          f'CMake must be installed to build the following extensions: {ext_names}'
      ) from e
    print('Found CMake')

  def build_extension(self, ext):
    """ This is where the CMake build happens. """
    name = ext.name
    DIM = name[-2]
    extension_dir = os.path.abspath(
        os.path.dirname(self.get_ext_fullpath(ext.name)))
    build_cfg = 'Debug' if self.debug else 'Release'
    cmake_args = [
        f'-DPython3_ROOT_DIR={sys.prefix}',
        f'-DPython3_EXECUTABLE={sys.executable}',
        f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extension_dir}',
        f'-DCMAKE_BUILD_TYPE={build_cfg}',
        f'-DMAKE_PYCY=ON',
        f'-DDIMENSION={DIM}' # Dimension of the simulation (2 or 3)
    ]
    if platform.system() != 'Windows':
      cmake_args.extend([
          f'-DPython3_LIBRARY={sysconfig.get_paths()["stdlib"]}',
          f'-DPython3_INCLUDE_DIR={sysconfig.get_paths()["include"]}',
      ])
    if platform.system() == 'Darwin' and os.environ.get('ARCHFLAGS'):
      osx_archs = []
      if '-arch x86_64' in os.environ['ARCHFLAGS']:
        osx_archs.append('x86_64')
      if '-arch arm64' in os.environ['ARCHFLAGS']:
        osx_archs.append('arm64')
      cmake_args.append(f'-DCMAKE_OSX_ARCHITECTURES={";".join(osx_archs)}')
    os.makedirs(self.build_temp, exist_ok=True)
    subprocess.check_call(
        ['cmake', ext.source_dir] + cmake_args, cwd=self.build_temp)
    subprocess.check_call(
        ['cmake', '--build', '.', f'-j{os.cpu_count()}', '--config', build_cfg],
        cwd=self.build_temp)

    # Force output to <extension_dir>/. Amends CMake multigenerator output paths
    # on Windows and avoids Debug/ and Release/ subdirs, which is CMake default.
    ct_dir = os.path.join(extension_dir, 'cytosim')  # pylint:disable=unreachable
    for cfg in ('Release', 'Debug'):
      cfg_dir = os.path.join(extension_dir, cfg)
      if os.path.isdir(cfg_dir):
        for f in os.listdir(cfg_dir):
          shutil.move(os.path.join(cfg_dir, f), ct_dir)
    # Moving the built executables to the package !
    parent = pathlib.Path(extension_dir).parent.absolute()
    for p in os.listdir(parent):
        pp = os.path.join(parent, p)
        if os.path.isdir(pp) and  p.startswith("temp."):
            for f in os.listdir(pp):
                ff = os.path.join(pp, f)
                if os.access(ff, os.X_OK):
                    if f=="sim%sD"%DIM:
                        pybin = os.path.join(extension_dir, "pycytoplay")
                        if not os.path.isdir(pybin):
                            os.mkdir(pybin)
                        shutil.move(ff, os.path.join(pybin, "wrapped_sim%sD"%DIM))
                    if f=="play%sD"%DIM:
                        pybin = os.path.join(extension_dir, "pycytoplay")
                        if not os.path.isdir(pybin):
                            os.mkdir(pybin)
                        shutil.move(ff, os.path.join(pybin, "wrapped_play%sD"%DIM))


if platform.system() != 'Windows':
    DIMS = [2,3]
    setup(
        name="cytoplay",
        version=version,
        packages=['pycytoplay'],
        include_package_data=True,
        package_dir={"": ".", "pycytoplay": "pycytoplay/package"},
        scripts=["pycytoplay/package/sim%sD"%DIM for DIM in DIMS].extend(
          ["pycytoplay/package/play%sD"%DIM for DIM in DIMS]),
        description=DOCLINES[0],
        long_description=open("README.md", encoding="utf8").read(),
        long_description_content_type="text/markdown",
        platforms=["Linux", "Mac OS-X", "Unix"],
        classifiers=[c for c in CLASSIFIERS.split("\n") if c],
        keywords="simulation actin microtubule polymer",
        cmdclass=dict(build_ext=BuildCMakeExtension),
        ext_modules=[CMakeExtension('cytoplay%sD'%DIM, source_dir='pycytoplay') for DIM in DIMS],
        zip_safe=False,
    )
else:
    setup(
        name='cytoplay',
        version=version,
        author="Serge Dmitrieff",
        description="A dummy package for windows",
        packages=['cytoplay'],
        package_dir={'cytoplay': 'dummy'},
    )
