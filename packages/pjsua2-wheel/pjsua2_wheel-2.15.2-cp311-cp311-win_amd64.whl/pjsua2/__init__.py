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
# We need to import from the pjsua2.py file in this package
import importlib.util
spec = importlib.util.spec_from_file_location("_pjsua2_module", os.path.join(_pkg_dir, "pjsua2.py"))
_pjsua2_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_pjsua2_module)

# Export all symbols from the module
import sys
_current_module = sys.modules[__name__]
for attr in dir(_pjsua2_module):
    if not attr.startswith('_'):
        setattr(_current_module, attr, getattr(_pjsua2_module, attr))

# Clean up
del _current_module, attr, spec, _pjsua2_module
os.environ['PATH'] = _old_path
del _old_path

__version__ = "2.15.2"