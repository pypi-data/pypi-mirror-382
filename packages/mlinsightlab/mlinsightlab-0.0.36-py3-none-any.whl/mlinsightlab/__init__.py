"""
Utilities for interacting with the Machine Learning Insights Lab (MLIL) platform.

This package is based around the 'MLIL_client' class, which has the capabilities to
interact with the functionality of the MLIL platform from a Python CLI environment.
"""

from .ModelManager import ModelManager
from .MLILClient import MLILClient

__all__ = ['MLILClient', 'ModelManager']
__version__ = '0.0.36'
