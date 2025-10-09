## shelldog/__init__.py

"""
Shelldog - Silent command tracker for development environments
"""

__version__ = "0.1.0"
__author__ = "Ansuman Bhujabala"
__license__ = "MIT"

from .logger import ShelldogLogger
from .shell_hook import ShellHook

__all__ = ["ShelldogLogger", "ShellHook"]