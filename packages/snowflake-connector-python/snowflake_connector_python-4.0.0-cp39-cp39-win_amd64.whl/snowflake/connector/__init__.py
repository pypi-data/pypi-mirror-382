#!/usr/bin/env python
# Python Db API v2
#
from __future__ import annotations


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'snowflake_connector_python.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-snowflake_connector_python-4.0.0')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-snowflake_connector_python-4.0.0')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

from functools import wraps

apilevel = "2.0"
threadsafety = 2
paramstyle = "pyformat"

import logging
from logging import NullHandler

from snowflake.connector.externals_utils.externals_setup import setup_external_libraries

from .connection import SnowflakeConnection
from .cursor import DictCursor
from .dbapi import (
    BINARY,
    DATETIME,
    NUMBER,
    ROWID,
    STRING,
    Binary,
    Date,
    DateFromTicks,
    Time,
    TimeFromTicks,
    Timestamp,
    TimestampFromTicks,
)
from .errors import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    _Warning,
)
from .log_configuration import EasyLoggingConfigPython
from .version import VERSION

logging.getLogger(__name__).addHandler(NullHandler())
setup_external_libraries()


@wraps(SnowflakeConnection.__init__)
def Connect(**kwargs) -> SnowflakeConnection:
    return SnowflakeConnection(**kwargs)


connect = Connect

SNOWFLAKE_CONNECTOR_VERSION = ".".join(str(v) for v in VERSION[0:3])
__version__ = SNOWFLAKE_CONNECTOR_VERSION

__all__ = [
    "SnowflakeConnection",
    # Error handling
    "Error",
    "_Warning",
    "InterfaceError",
    "DatabaseError",
    "NotSupportedError",
    "DataError",
    "IntegrityError",
    "ProgrammingError",
    "OperationalError",
    "InternalError",
    # Extended cursor
    "DictCursor",
    # DBAPI PEP 249 required exports
    "connect",
    "apilevel",
    "threadsafety",
    "paramstyle",
    "Date",
    "Time",
    "Timestamp",
    "Binary",
    "DateFromTicks",
    "TimeFromTicks",
    "TimestampFromTicks",
    "STRING",
    "BINARY",
    "NUMBER",
    "DATETIME",
    "ROWID",
    # Extended data type (experimental)
    "EasyLoggingConfigPython",
]
