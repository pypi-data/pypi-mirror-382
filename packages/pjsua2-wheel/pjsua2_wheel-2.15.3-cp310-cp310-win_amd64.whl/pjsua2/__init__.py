"""
PJSUA2 - Python bindings for PJSIP

This is a standalone wheel that includes the Visual C++ Runtime DLLs.
No additional installation of Visual C++ Redistributable is required.

Usage:
    import pjsua2 as pj
    
    ep = pj.Endpoint()
    ep.libCreate()
    # ... your SIP code ...
"""

import os
import sys

# Add the package directory to DLL search path (Python 3.8+)
if sys.version_info >= (3, 8):
    # Get the directory where this package is installed
    _pkg_dir = os.path.dirname(__file__)
    # Add it to the DLL search path so Windows can find the bundled DLLs
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(_pkg_dir)

# For older Python or as a fallback, temporarily add to PATH
_pkg_dir = os.path.dirname(__file__)
_old_path = os.environ.get('PATH', '')
os.environ['PATH'] = _pkg_dir + os.pathsep + _old_path

# Import everything from the pjsua2 module
# First, ensure the package directory is in sys.path so _pjsua2.pyd can be found
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

# Now import from pjsua2.py which will be able to find _pjsua2.pyd
from .pjsua2 import *

# Clean up
os.environ['PATH'] = _old_path
del _old_path, _pkg_dir

__version__ = "2.15.3"