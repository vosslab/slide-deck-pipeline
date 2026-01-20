"""
Pytest config to ensure local imports work without installation.
"""

# Standard Library
import os
import sys

#============================================


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
if TESTS_DIR not in sys.path:
	sys.path.insert(0, TESTS_DIR)
