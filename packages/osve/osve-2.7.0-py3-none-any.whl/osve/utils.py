#*****************************************************************************#
# This file is subject to the terms and conditions defined in the             #
# file 'LICENSE.txt', which is part of this source code package.              #
#                                                                             #
# No part of the package, including this file, may be copied, modified,       #
# propagated, or distributed except according to the terms contained in       #
# the file 'LICENSE.txt'.                                                     #
#                                                                             #
# (C) Copyright European Space Agency, 2025                                   #
#*****************************************************************************# 


"""
Created on July, 2023

@author: Ricardo Valles Blanco (ESAC)

This module contains different utility functions for OSVE.
"""

import os
import sys
import sysconfig
import platform

DELIVERIES_PATH="deliveries"


def get_platform():
    """
    Returns a string with the current platform (system and machine architecture).

    This function attempts to improve upon `sysconfig.get_platform` by fixing some
    issues when running a Python interpreter with a different architecture than
    that of the system (e.g., 32-bit on 64-bit system or a multiarch build),
    which should return the machine architecture of the currently running
    interpreter rather than that of the system (which didn't seem to work
    properly). The reported machine architectures follow platform-specific
    naming conventions (e.g., "x86_64" on Linux, but "x64" on Windows).

    Example output strings for common platforms:

        darwin_(ppc|ppc64|i368|x86_64|arm64)
        linux_(i686|x86_64|armv7l|aarch64)
        windows_(x86|x64|arm32|arm64)

    :return: The platform string.
    :rtype: str
    """
    system = platform.system().lower()
    machine = sysconfig.get_platform().split("-")[-1].lower()
    is_64bit = sys.maxsize > 2 ** 32

    if system == "darwin":  # get machine architecture of multiarch binaries
        mac_os_version, _, _ = platform.mac_ver()
        if mac_os_version:
            machine = platform.machine().lower()

    elif system == "linux":  # fix running 32bit interpreter on 64bit system
        if not is_64bit and machine == "x86_64":
            machine = "i686"
        elif not is_64bit and machine == "aarch64":
                machine = "armv7l"

    elif system == "windows": # return more precise machine architecture names
        if machine == "amd64":
            machine = "x64"
        elif machine == "win32":
            if is_64bit:
                machine = platform.machine().lower()
            else:
                machine = "x86"

    # some more fixes based on examples in https://en.wikipedia.org/wiki/Uname
    if not is_64bit and machine in ("x86_64", "amd64"):
        if any([x in system for x in ("cygwin", "mingw", "msys")]):
            machine = "i686"
        else:
            machine = "i386"

    return f"{system}_{machine}"


def build_lib_path():
    """
    Returns the path of the OSVE library included in the OSVE Python package
    depending on the OS platform.

    :return: The path of the OSVE library.
    :rtype: str
    """
    here = os.path.abspath(os.path.dirname(__file__))

    if_shared_lib_name = None
    my_platform = get_platform()
    if (my_platform.startswith("linux")):
        if_shared_lib_name = os.path.join("lin", "libosve-if.so")

    elif (my_platform.startswith("darwin")):
       
        if ("arm64" in my_platform):
            if_shared_lib_name = os.path.join("mac", "arm64", "libosve-if.dylib")
            
        elif ("x86_64" in my_platform):
            if_shared_lib_name = os.path.join("mac", "x86_64", "libosve-if.dylib")

    elif (my_platform.startswith("windows")):
        if_shared_lib_name = os.path.join("win", "osve-if.dll")

    if if_shared_lib_name is None:
        raise Exception("Unsupported OS platform: " + my_platform)

    return os.path.join(here, DELIVERIES_PATH, if_shared_lib_name)


def get_version(version_file, version_key):
    """
    Returns the version string referenced by a version_key contained in a version_file.

    :param version_file: The file containing version information.
    :type version_file: str
    :param version_key: The key to identify the version.
    :type version_key: str
    :return: The version string.
    :rtype: str
    """
    version_file = open(version_file, 'r')

    for line in version_file.readlines():
        if line.startswith(version_key):
            return line.split("=")[1].strip()

    raise Exception(version_key + " not found in " + version_file)