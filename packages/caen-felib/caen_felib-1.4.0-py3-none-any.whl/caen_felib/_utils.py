"""
@ingroup Python
"""

__author__ = 'Giovanni Cerretani'
__copyright__ = 'Copyright (C) 2023 CAEN SpA'
__license__ = 'LGPL-3.0-or-later'
# SPDX-License-Identifier: LGPL-3.0-or-later

import ctypes as ct
import sys
from abc import ABC, abstractmethod
from typing import Any, Optional, Union, overload

if sys.platform == 'win32':
    _LibNotFoundClass = FileNotFoundError
else:
    _LibNotFoundClass = OSError


class Lib(ABC):
    """
    This class loads the shared library and exposes its functions on its
    public attributes using ctypes.
    """

    def __init__(self, name: str, stdcall: bool = True) -> None:
        self.__name = name
        self.__stdcall = stdcall  # Ignored on Linux
        self.__load_lib()

    def __load_lib(self) -> None:
        """
        Variadic functions are __cdecl even if declared as __stdcall.
        This difference applies only to 32 bit applications, 64 bit
        applications have its own calling convention.
        """
        self.__lib_variadic: ct.CDLL
        if sys.platform == 'win32':
            self.__lib: Union[ct.CDLL, ct.WinDLL]
        else:
            self.__lib: ct.CDLL

        # Load library
        try:
            if sys.platform == 'win32':
                self.__path = f'{self.name}.dll'
                if self.__stdcall:
                    self.__lib = ct.windll.LoadLibrary(self.__path)
                    self.__lib_variadic = ct.cdll.LoadLibrary(self.__path)
                else:
                    self.__lib = ct.cdll.LoadLibrary(self.__path)
                    self.__lib_variadic = self.__lib
            else:
                self.__path = f'lib{self.name}.so'
                self.__lib = ct.cdll.LoadLibrary(self.__path)
                self.__lib_variadic = self.__lib

        except _LibNotFoundClass as ex:
            raise RuntimeError(
                f'Library {self.name} not found. This module requires '
                'the latest version of the library to be installed on '
                'your system. You may find the official installers at '
                'https://www.caen.it/. Please install it and retry.'
            ) from ex

    @property
    def name(self) -> str:
        """Name of the shared library"""
        return self.__name

    @property
    def path(self) -> Any:
        """Path of the shared library"""
        return self.__path

    @abstractmethod
    def sw_release(self) -> str:
        """Get software release version"""

    def ver_at_least(self, target: tuple[int, ...]) -> bool:
        """Check if the library version is at least the target"""
        ver = self.sw_release()
        return version_to_tuple(ver) >= target

    def get(self, name: str, variadic: bool = False):
        """Get function by name"""
        if variadic:
            return self.__lib_variadic[name]
        return self.__lib[name]

    # Python utilities

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.path})'

    def __str__(self) -> str:
        return self.path


def version_to_tuple(version: str) -> tuple[int, ...]:
    """Version string in the form N.N.N to tuple (N, N, N)"""
    return tuple(map(int, version.split('.')))


def to_bytes(path: str) -> bytes:
    """Convert string to bytes"""
    return path.encode('ascii')


@overload
def to_bytes_opt(path: None) -> None: ...
@overload
def to_bytes_opt(path: str) -> bytes: ...


def to_bytes_opt(path: Optional[str]) -> Optional[bytes]:
    """Convert string to bytes"""
    return None if path is None else to_bytes(path)


# Slots brings some performance improvements and memory savings.
# In caen_felib slots are also a trick to prevent users from trying to
# set Node values using the `__setattr__` method instead of the value
# attribute.
if sys.version_info >= (3, 10):
    dataclass_slots = {'slots': True}
else:
    dataclass_slots = {}


# Weakref support is required by the cache manager.
if sys.version_info >= (3, 11):
    dataclass_slots_weakref = dataclass_slots | {'weakref_slot': True}
else:
    dataclass_slots_weakref = {}
