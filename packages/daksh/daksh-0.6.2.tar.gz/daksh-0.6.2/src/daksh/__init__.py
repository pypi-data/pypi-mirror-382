"""Top-level package for DAKSH."""

__all__ = [
    '__version__',
    '__author__',
    '__email__',
    'cli',
    'health',
    'io'
]

__author__ = """Yeshwanth Reddy"""
__email__ = 'yeshwanth@divami.com'
__version__ = '0.1.0'

from .__pre_init__ import cli
from .health import *
from .update_prompts import *