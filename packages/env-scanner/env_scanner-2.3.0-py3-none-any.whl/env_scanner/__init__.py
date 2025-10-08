"""
Env Scanner

Automatically scans Python projects to find environment variables and generates .env-example files.
"""

__version__ = "2.3.0"
__author__ = "Ammar Munir"
__email__ = "ammarmunir4567@gmail.com"

# Import main functionality to make it available at package level
from .scanner import EnvScanner
from .generator import EnvExampleGenerator

__all__ = [
    "EnvScanner",
    "EnvExampleGenerator",
]
