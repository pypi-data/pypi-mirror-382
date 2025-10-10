#! /usr/bin/env python3

################################################################################
""" Legacy compatibility module for process.py API.
    This module provides backward compatibility for existing code that used
    the original process.py module. The actual implementation has been moved
    to thingy.run with enhanced capabilities.
"""
################################################################################

from thingy.run import run_process, RunError

# Provide the same API as the original process.py
def run(command, foreground=False, shell=False):
    """
    Run a command with the original process.py API.

    Args:
        command: Command to run (string or list)
        foreground: If True, run in foreground with output to console
        shell: Whether to use shell for execution

    Returns:
        List of output lines (empty if foreground=True)

    Raises:
        RunError: If command fails
    """
    return run_process(command, foreground=foreground, shell=shell)

# Re-export RunError for compatibility
__all__ = ['run', 'RunError']
