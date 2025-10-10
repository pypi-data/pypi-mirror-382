from .starlark import *

__doc__ = starlark.__doc__
if hasattr(starlark, "__all__"):
    __all__ = starlark.__all__