# -*- coding: utf-8 -*-
# Only export the public submodule name
__all__ = ["boltznet_tf"]


from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("boltznet")
except PackageNotFoundError:
    __version__ = "unknown"