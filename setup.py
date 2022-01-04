#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (c) 2019 by Lowatt info@lowatt.fr
#
# This program is part of lowatt_enedis, which is *NOT* free software.

from setuptools import setup


def local_scheme(version: str) -> str:
    """Generate a PEP440 compatible version if PEP440_VERSION is enabled"""
    import os

    import setuptools_scm.version  # only present during setup time

    if "PEP440_VERSION" in os.environ:
        return ""
    version = setuptools_scm.version.get_local_node_and_date(version)
    assert isinstance(version, str), version
    return version


if __name__ == "__main__":
    setup(use_scm_version={"local_scheme": local_scheme})
