"""
run_r: Execute R scripts from Python and retrieve workspace variables.

This package provides a simple interface to run R scripts and extract all variables
from the R workspace after execution.
"""

from .run_r import run_r_script, RScriptRunner, find_rscript

__version__ = "0.2.0"
__all__ = ["run_r_script", "RScriptRunner", "find_rscript"]
