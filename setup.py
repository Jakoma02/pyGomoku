#!/usr/bin/env python3

"""
Setuptools install script
"""

from setuptools import setup, find_packages

setup(
    name="pyGomoku",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "wheel",
    ],

    author="Jakub Komárek",
    author_email="komaja@email.cz",
    description="Python gomoku game",

    entry_points="""
        [gui_scripts]
        pygomoku=pygomoku.main:main
        """
)
