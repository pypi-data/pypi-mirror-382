from __future__ import annotations
from netgen.libngpy._meshing import _Redraw
from pathlib import Path
from pyngcore.pyngcore import Timer
import sys
from . import config
from . import libngpy
__all__: list[str] = ['Path', 'Redraw', 'TimeFunction', 'Timer', 'config', 'libngpy', 'load_occ_libs', 'v']
def Redraw(*args, **kwargs):
    ...
def TimeFunction(func, name = None):
    ...
def _check_python_version():
    ...
def _get_diagnostics():
    ...
def load_occ_libs():
    ...
__diagnostics_template: str = '\nNetgen diagnostics:\n    sys.platform:          {sys.platform}\n    sys.executable:        {sys.executable}\n    sys.version:           {sys.version}\n    Netgen python version: {config.PYTHON_VERSION}\n    Netgen path            {__file__}\n    Netgen config          {config.__file__}\n    Netgen version         {config.NETGEN_VERSION}\n    sys.path: {sys.path}\n'
_netgen_bin_dir: str = 'C:\\gitlabci\\tools\\builds\\3zsqG5ns\\0\\ngsolve\\netgen\\_skbuild\\win-amd64-3.14\\cmake-install\\netgen'
_netgen_lib_dir: str = 'C:\\gitlabci\\tools\\builds\\3zsqG5ns\\0\\ngsolve\\netgen\\_skbuild\\win-amd64-3.14\\cmake-install\\netgen'
v: sys.version_info  # value = sys.version_info(major=3, minor=14, micro=0, releaselevel='final', serial=0)
