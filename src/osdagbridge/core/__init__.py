"""Core package for OsdagBridge.

The previous version re-exported `from .models import *`, but no `models`
module exists in this package, so importing `osdagbridge.core` — or anything
beneath it — raised ModuleNotFoundError. The star import is removed rather
than replaced: submodules are imported explicitly by the code that needs
them, which keeps import cost low and avoids re-export ambiguity.
"""
